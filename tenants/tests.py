from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from accounts.models import Institution, User
from departments.models import Department
from tenants.models import SubscriptionPlan, TenantSubscription


class TenantIsolationTests(TestCase):
    def setUp(self):
        self.plan = SubscriptionPlan.objects.get(code="basic")
        self.institution_a = Institution.objects.create(name="College A", code="college-a")
        self.institution_b = Institution.objects.create(name="College B", code="college-b")
        TenantSubscription.objects.create(
            institution=self.institution_a,
            plan=self.plan,
            status=TenantSubscription.ACTIVE,
            expires_at=timezone.now() + timedelta(days=30),
            max_students_override=1,
            max_teachers_override=1,
        )
        TenantSubscription.objects.create(
            institution=self.institution_b,
            plan=self.plan,
            status=TenantSubscription.ACTIVE,
            expires_at=timezone.now() + timedelta(days=30),
            max_students_override=1,
            max_teachers_override=1,
        )
        self.user_a = User.objects.create_user(
            username="admin-a",
            password="admin12345",
            role=User.ADMIN,
            institution=self.institution_a,
        )
        self.user_b = User.objects.create_user(
            username="admin-b",
            password="admin12345",
            role=User.ADMIN,
            institution=self.institution_b,
        )
        self.department_a = Department.objects.create(name="Engineering", institution=self.institution_a)
        self.department_b = Department.objects.create(name="Medical", institution=self.institution_b)

    def _client_for(self, username, password):
        client = APIClient(HTTP_HOST="127.0.0.1:8000")
        response = client.post("/api/login/", {"username": username, "password": password}, format="json")
        token = response.json()["token"]
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        return client

    def test_tenant_admin_cannot_see_other_tenant_departments(self):
        client = self._client_for("admin-a", "admin12345")
        response = client.get("/api/departments/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["name"], "Engineering")

    def test_student_limit_is_enforced(self):
        client = self._client_for("admin-a", "admin12345")
        first = client.post(
            "/api/students/",
            {"name": "Student One", "email": "one@example.com", "year": 1, "department": self.department_a.id},
            format="json",
        )
        self.assertEqual(first.status_code, 201)
        second = client.post(
            "/api/students/",
            {"name": "Student Two", "email": "two@example.com", "year": 1, "department": self.department_a.id},
            format="json",
        )
        self.assertEqual(second.status_code, 400)

    def test_teacher_limit_is_enforced(self):
        client = self._client_for("admin-a", "admin12345")
        first = client.post(
            "/api/teachers/",
            {"name": "Teacher One", "email": "teacher1@example.com", "phone": "1", "department": self.department_a.id},
            format="json",
        )
        self.assertEqual(first.status_code, 201)
        second = client.post(
            "/api/teachers/",
            {"name": "Teacher Two", "email": "teacher2@example.com", "phone": "2", "department": self.department_a.id},
            format="json",
        )
        self.assertEqual(second.status_code, 400)

    def test_super_admin_can_create_school_tenant(self):
        User.objects.create_user(
            username="superadmin-test",
            password="super12345",
            role=User.SUPER_ADMIN,
            is_staff=True,
            is_superuser=True,
        )
        client = self._client_for("superadmin-test", "super12345")
        response = client.post(
            "/api/tenants/institutions/",
            {
                "institution_name": "Sunrise Public School",
                "institution_code": "sunrise-school",
                "institution_type": "school",
                "admin_name": "School Admin",
                "admin_username": "schooladmin",
                "admin_email": "schooladmin@example.com",
                "password": "school12345",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["institution_type"], "school")
