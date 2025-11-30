from django.test import TestCase
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from rest_framework.test import APIClient
from rest_framework import status
from users.models import User
from .models import Specialty, CourseStream, Topic, TopicSubmission


class DatabaseIntegrityTests(TestCase):
    def setUp(self):
        self.specialty = Specialty.objects.create(code="121", name="Інженерія програмного забезпечення")
        self.teacher = User.objects.create_user(
            email="teacher@test.com", password="password", first_name="Test", last_name="Teacher", role='TEACHER'
        )

    def test_foreign_key_constraint_for_topic_and_stream(self):
        with self.assertRaises((IntegrityError, ValidationError)):
            Topic.objects.create(
                title="Тема без потоку",
                description="Опис",
                teacher=self.teacher,
            )

    def test_cascade_delete_from_stream_to_topics(self):
        stream = CourseStream.objects.create(name="Потік 2023", specialty=self.specialty, academic_year="2023-2024", semester=1, course_number=4)
        Topic.objects.create(title="Тема 1", description="Опис 1", teacher=self.teacher, stream=stream)
        Topic.objects.create(title="Тема 2", description="Опис 2", teacher=self.teacher, stream=stream)
        self.assertEqual(Topic.objects.count(), 2)
        stream.delete()
        self.assertEqual(Topic.objects.count(), 0)

    def test_field_max_length_constraint(self):
        long_title = "a" * 256
        with self.assertRaises(ValidationError):
            topic = Topic(
                title=long_title,
                description="Some description",
                teacher=self.teacher,
                stream=CourseStream.objects.create(name="Some Stream", specialty=self.specialty, academic_year="2023-2024", semester=1, course_number=4)
            )
            topic.full_clean()

    def test_specialty_code_is_unique(self):
        with self.assertRaises(IntegrityError):
            Specialty.objects.create(code="121", name="Комп'ютерні науки")


class StudentSubmissionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.teacher = User.objects.create_user(email="teacher@test.com", password="password123", first_name="Test", last_name="Teacher", role='TEACHER')
        self.student1 = User.objects.create_user(email="student1@test.com", password="password123", first_name="Student", last_name="One", role='STUDENT')
        self.specialty = Specialty.objects.create(code="121", name="Інженерія програмного забезпечення")
        self.stream = CourseStream.objects.create(name="Потік 2023", specialty=self.specialty, academic_year="2023-2024", semester=1, course_number=4)
        self.stream.students.add(self.student1)
        self.available_topic = Topic.objects.create(title="Доступна тема", description="Опис", teacher=self.teacher, stream=self.stream)
        self.taken_topic = Topic.objects.create(title="Зайнята тема", description="Опис", teacher=self.teacher, stream=self.stream, status='TAKEN')

    def test_student_can_create_submission_for_available_topic(self):
        self.client.login(email="student1@test.com", password="password123")
        response = self.client.post('/api/courses/submissions/create/', {'topic_id': self.available_topic.id, 'student_vision': 'My vision'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(TopicSubmission.objects.filter(student=self.student1, topic=self.available_topic).exists())

    def test_student_cannot_create_submission_for_taken_topic(self):
        self.client.login(email="student1@test.com", password="password123")
        response = self.client.post('/api/courses/submissions/create/', {'topic_id': self.taken_topic.id, 'student_vision': 'My vision'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Topic is not available', response.data['detail'])

    def test_student_cannot_create_second_submission_in_same_stream(self):
        TopicSubmission.objects.create(student=self.student1, topic=self.available_topic, status='PENDING')
        another_topic = Topic.objects.create(title="Інша тема", description="Опис", teacher=self.teacher, stream=self.stream)
        self.client.login(email="student1@test.com", password="password123")
        response = self.client.post('/api/courses/submissions/create/', {'topic_id': another_topic.id, 'student_vision': 'My vision'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('You already have a pending or approved submission in this stream.', response.data['detail'])


class TeacherSubmissionManagementTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.teacher = User.objects.create_user(email="teacher@test.com", password="password123", first_name="Test", last_name="Teacher", role='TEACHER')
        self.student1 = User.objects.create_user(email="student1@test.com", password="password123", first_name="Student", last_name="One", role='STUDENT')
        self.student2 = User.objects.create_user(email="student2@test.com", password="password123", first_name="Student", last_name="Two", role='STUDENT')
        self.specialty = Specialty.objects.create(code="121", name="Інженерія програмного забезпечення")
        self.stream = CourseStream.objects.create(name="Потік 2023", specialty=self.specialty, academic_year="2023-2024", semester=1, course_number=4)
        self.stream.students.add(self.student1, self.student2)
        self.available_topic = Topic.objects.create(title="Доступна тема", description="Опис", teacher=self.teacher, stream=self.stream)

    def test_teacher_can_approve_submission(self):
        submission1 = TopicSubmission.objects.create(student=self.student1, topic=self.available_topic, status='PENDING')
        submission2 = TopicSubmission.objects.create(student=self.student2, topic=self.available_topic, status='PENDING')
        self.client.login(email="teacher@test.com", password="password123")
        response = self.client.post(f'/api/courses/submissions/{submission1.id}/approve/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        submission1.refresh_from_db()
        submission2.refresh_from_db()
        self.available_topic.refresh_from_db()
        self.assertEqual(submission1.status, 'APPROVED')
        self.assertEqual(submission2.status, 'REJECTED')
        self.assertEqual(self.available_topic.status, 'TAKEN')
        
    def test_teacher_can_reject_submission(self):
        submission = TopicSubmission.objects.create(student=self.student1, topic=self.available_topic, status='PENDING')
        self.client.login(email="teacher@test.com", password="password123")
        response = self.client.post(f'/api/courses/submissions/{submission.id}/reject/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        submission.refresh_from_db()
        self.available_topic.refresh_from_db()
        self.assertEqual(submission.status, 'REJECTED')
        self.assertEqual(self.available_topic.status, 'AVAILABLE')