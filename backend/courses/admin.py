from .models import Specialty, CourseStream, Topic, TopicSubmission
from users.models import User
from django.contrib import admin
from django.urls import path, reverse
from django.utils.html import format_html
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction
from django.utils.crypto import get_random_string
import csv
import io


@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'teacher', 'stream', 'status')
    list_filter = ('status', 'stream', 'teacher')
    search_fields = ('title', 'description')


@admin.register(TopicSubmission)
class TopicSubmissionAdmin(admin.ModelAdmin):
    list_display = ('topic', 'student', 'status', 'created_at')
    list_filter = ('status',)
    autocomplete_fields = ('topic', 'student')
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {
            'fields': ('topic', 'student', 'status', 'student_vision', 'created_at')
        }),
    )


@admin.register(CourseStream)
class CourseStreamAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "specialty",
        "course_number",
        "semester",
        "academic_year",
        "is_active",
        "import_users_link",
    )
    list_filter = ("is_active", "specialty", "academic_year", "semester")
    search_fields = ("name", "users__email", "users__first_name", "users__last_name")
    autocomplete_fields = ("users",)
    actions = ["deactivate_streams"]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<path:object_id>/import/",
                self.admin_site.admin_view(self.import_users_view),
                name="courses_coursestream_import_users",
            ),
        ]
        return custom_urls + urls

    def import_users_link(self, obj):
        url = reverse("admin:courses_coursestream_import_users", args=[obj.pk])
        return format_html('<a href="{}">Import Users</a>', url)

    import_users_link.short_description = "Import Participants"

    @admin.action(description="Deactivate selected streams")
    def deactivate_streams(self, request, queryset):
        updated_count = queryset.update(is_active=False)
        self.message_user(
            request,
            f"{updated_count} streams have been successfully deactivated",
            messages.SUCCESS,
        )

    def import_users_view(self, request, object_id):
        stream = self.get_object(request, object_id)
        changelist_url = reverse("admin:courses_coursestream_changelist")

        if request.method == "POST" and "file" in request.FILES:
            file = request.FILES["file"]
            if not file.name.endswith(".csv"):
                self.message_user(request, "Please upload a valid .csv file", messages.ERROR)
                return redirect(changelist_url)

            try:
                self.import_users_from_csv(request, stream, file)
            except Exception as e:
                self.message_user(request, f"Error processing file: {e}", messages.ERROR)
                return redirect(changelist_url)

            return redirect(changelist_url)

        context = self.admin_site.each_context(request)
        context["opts"] = self.model._meta
        context["stream"] = stream

        return render(request, "admin/import_users_form.html", context)

    @transaction.atomic
    def import_users_from_csv(self, request, stream, file):
        decoded_file = file.read().decode("utf-8")
        io_string = io.StringIO(decoded_file)
        reader = csv.DictReader(io_string)
        
        imported_count = 0
        for row in reader:
            email = row.get("email")
            if not email:
                continue

            defaults = {
                "first_name": row.get("first_name", ""),
                "last_name": row.get("last_name", ""),
                "middle_name": row.get("middle_name", ""),
                "role": row.get("role", "").upper()
            }
            
            if not User.objects.filter(email=email).exists():
                 if not all([defaults["first_name"], defaults["last_name"], defaults["middle_name"], defaults["role"]]):
                    self.message_user(request, f"Skipping user {email}: missing required fields (first_name, last_name, middle_name, role)", messages.WARNING)
                    continue

            user, created = User.objects.get_or_create(email=email, defaults=defaults)

            if created:
                password = get_random_string(12)
                user.set_password(password)
                user.save()
                
                try:
                    send_mail(
                        "Account created for 'eKafedra'",
                        f"Your account has been created\nLogin: {user.email}\nPassword: {password}",
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                        fail_silently=False,
                    )
                except Exception as e:
                    print(f"Failed to send email to {user.email}: {e}")

            if user not in stream.users.all():
                stream.users.add(user)
                imported_count += 1
        
        if imported_count > 0:
            self.message_user(request, f"Successfully processed file. Added {imported_count} new participants to the stream", messages.SUCCESS)
        else:
            self.message_user(request, "File processed. No new participants were added to the stream (they might be already in it)", messages.INFO)