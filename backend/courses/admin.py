from .models import Specialty, CourseStream, Topic, TopicSubmission
from users.models import User
from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction
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


@admin.register(CourseStream)
class CourseStreamAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "specialty",
        "course_number",
        "semester",
        "academic_year",
        "is_active",
    )
    list_filter = ("is_active", "specialty", "academic_year", "semester")
    search_fields = ("name",)
    filter_horizontal = ("users",)

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

    def import_users_view(self, request, object_id):
        stream = self.get_object(request, object_id)
        if request.method == "POST" and "file" in request.FILES:
            file = request.FILES["file"]
            if not file.name.endswith(".csv"):
                self.message_user(
                    request, "Please upload a valid .csv file", messages.ERROR
                )
                return redirect(".")

            try:
                self.import_users_from_csv(request, stream, file)
            except Exception as e:
                self.message_user(request, f"Error processing file: {e}", messages.ERROR)
                return redirect(".")

            return redirect("..")

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
                "last_name": row.get("last_name", ""),
                "first_name": row.get("first_name", ""),
                "middle_name": row.get("middle_name", ""),
                "role": row.get("role", "").upper(),
            }
            
            user, created = User.objects.get_or_create(email=email, defaults=defaults)

            if created:
                password = User.objects.make_random_password()
                user.set_password(password)
                user.save()
                
                try:
                    send_mail(
                        "Account created for 'eKafedra'",
                        f"Your account has been created.\nLogin: {user.email}\nPassword: {password}",
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                        fail_silently=False,
                    )
                except Exception as e:
                    print(f"Failed to send email to {user.email}: {e}")

            if user not in stream.users.all():
                stream.users.add(user)
                imported_count += 1

        self.message_user(request, f"Successfully imported {imported_count} users.", messages.SUCCESS)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["has_import_permission"] = self.has_change_permission(request)
        return super().changelist_view(request, extra_context=extra_context)