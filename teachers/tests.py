from datetime import timedelta
from unittest.mock import patch
from django.core.files.uploadedfile import SimpleUploadedFile

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from accounts.models import Institution, User
from departments.models import Department
from tenants.models import SubscriptionPlan, TenantSubscription


class TeacherMessagingTests(TestCase):
    def setUp(self):
        self.plan = SubscriptionPlan.objects.get(code="basic")
        self.institution = Institution.objects.create(name="College A", code="college-a")
        TenantSubscription.objects.create(
            institution=self.institution,
            plan=self.plan,
            status=TenantSubscription.ACTIVE,
            expires_at=timezone.now() + timedelta(days=30),
            max_teachers_override=5,
        )
        self.admin = User.objects.create_user(
            username="admin-a",
            password="admin12345",
            role=User.ADMIN,
            institution=self.institution,
        )
        self.department = Department.objects.create(name="Engineering", institution=self.institution)
        self.client = APIClient(HTTP_HOST="127.0.0.1:8000")
        response = self.client.post(
            "/api/login/",
            {"username": "admin-a", "password": "admin12345"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.json()['token']}")

    @patch("teachers.serializers.send_teacher_credentials")
    def test_create_teacher_sends_credentials_message(self, send_teacher_credentials):
        response = self.client.post(
            "/api/teachers/",
            {
                "name": "Teacher One",
                "email": "teacher1@example.com",
                "phone": "+15550001111",
                "department": self.department.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["generated_password"], "default123")
        teacher_user = User.objects.get(username="teacher1@example.com")
        self.assertEqual(teacher_user.role, User.TEACHER)
        send_teacher_credentials.assert_called_once()

    @patch("teachers.serializers.send_teacher_credentials")
    def test_upload_teachers_csv(self, send_teacher_credentials):
        csv_content = "name,email,phone,department\nTeacher One,teacher1@example.com,+15550001111,Engineering\n"
        upload = SimpleUploadedFile("teachers.csv", csv_content.encode("utf-8"), content_type="text/csv")

        response = self.client.post("/api/teachers/upload/", {"file": upload})

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["teachers_created"], 1)
        self.assertTrue(User.objects.filter(username="teacher1@example.com").exists())
        send_teacher_credentials.assert_called_once()

    @patch("teachers.serializers.send_teacher_credentials")
    def test_upload_teachers_csv_accepts_capitalized_headers(self, send_teacher_credentials):
        csv_content = "Name,Email,Phone,Department\nTeacher One,teacher1@example.com,+15550001111,Engineering\n"
        upload = SimpleUploadedFile("teachers.csv", csv_content.encode("utf-8"), content_type="text/csv")

        response = self.client.post("/api/teachers/upload/", {"file": upload})

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["teachers_created"], 1)
        send_teacher_credentials.assert_called_once()
