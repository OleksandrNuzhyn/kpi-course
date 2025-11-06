from django.db import models
from django.conf import settings


class Specialty(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name} ({self.code})"


class CourseStream(models.Model):
    name = models.CharField(max_length=255)
    academic_year = models.CharField(max_length=10)
    semester = models.IntegerField()
    course_number = models.IntegerField()
    specialty = models.ForeignKey(Specialty, on_delete=models.PROTECT)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="streams", blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Topic(models.Model):
    class TopicStatus(models.TextChoices):
        AVAILABLE = "AVAILABLE", "Available"
        TAKEN = "TAKEN", "Taken"

    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=10, choices=TopicStatus.choices, default=TopicStatus.AVAILABLE)
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, limit_choices_to={"role": "TEACHER"}, related_name="topics")
    stream = models.ForeignKey(CourseStream, on_delete=models.CASCADE, related_name="topics")

    def __str__(self):
        return self.title


class TopicSubmission(models.Model):
    class SubmissionStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    status = models.CharField(max_length=10, choices=SubmissionStatus.choices, default=SubmissionStatus.PENDING)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={"role": "STUDENT"}, related_name="submissions")
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="submissions")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Submission for "{self.topic.title}" by {self.student.email}'