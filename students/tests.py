from datetime import timedelta
from django.core.files.uploadedfile import SimpleUploadedFile

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from accounts.models import Institution, User
from departments.models import Department
from tenants.models import SubscriptionPlan, TenantSubscription


class StudentProvisioningTests(TestCase):
    def setUp(self):
        self.plan = SubscriptionPlan.objects.get(code="basic")
        self.institution = Institution.objects.create(name="College A", code="college-a")
        TenantSubscription.objects.create(
            institution=self.institution,
            plan=self.plan,
            status=TenantSubscription.ACTIVE,
            expires_at=timezone.now() + timedelta(days=30),
            max_students_override=5,
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

    def test_create_student_creates_login_account(self):
        response = self.client.post(
            "/api/students/",
            {
                "name": "Student One",
                "email": "student1@example.com",
                "year": 1,
                "department": self.department.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["generated_password"], "default123")
        student_user = User.objects.get(username="student1@example.com")
        self.assertEqual(student_user.role, User.STUDENT)
        self.assertEqual(student_user.institution_id, self.institution.id)

    def test_upload_students_csv(self):
        csv_content = "name,email,year,department\nStudent One,student1@example.com,1,Engineering\n"
        upload = SimpleUploadedFile("students.csv", csv_content.encode("utf-8"), content_type="text/csv")

        response = self.client.post("/api/students/upload/", {"file": upload})

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["students_created"], 1)
        self.assertTrue(User.objects.filter(username="student1@example.com").exists())
