from datetime import date

from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import Institution, User
from departments.models import Department
from attendance.models import Attendance
from results.models import Result
from students.models import Student
from subjects.models import Subject
from teachers.models import Teacher

from .models import AIChat


class AIChatAPITests(APITestCase):
    def setUp(self):
        self.institution = Institution.objects.create(name="North Campus", code="north-campus")
        self.department = Department.objects.create(institution=self.institution, name="Science")

        self.teacher_user = User.objects.create_user(
            username="teacher1",
            password="pass1234",
            role="teacher",
            institution=self.institution,
        )
        self.teacher = Teacher.objects.create(
            institution=self.institution,
            name="Teacher One",
            email="teacher1@example.com",
            department=self.department,
            user=self.teacher_user,
        )

        self.student_user = User.objects.create_user(
            username="student1",
            password="pass1234",
            role="student",
            institution=self.institution,
        )
        self.student = Student.objects.create(
            institution=self.institution,
            name="Student One",
            email="student1@example.com",
            year=2,
            department=self.department,
            user=self.student_user,
        )

        self.subject = Subject.objects.create(
            institution=self.institution,
            name="Physics",
            department=self.department,
            teacher=self.teacher,
        )
        Attendance.objects.create(
            institution=self.institution,
            student=self.student,
            subject=self.subject,
            date=date(2026, 5, 1),
            status=Attendance.PRESENT,
        )
        Attendance.objects.create(
            institution=self.institution,
            student=self.student,
            subject=self.subject,
            date=date(2026, 5, 2),
            status=Attendance.ABSENT,
        )
        Result.objects.create(
            institution=self.institution,
            student=self.student,
            subject=self.subject,
            marks=83,
        )
        self.url = "/api/ai/chat/"

    def test_requires_authentication(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_student_chat_creates_history_and_returns_fallback_summary(self):
        self.client.force_authenticate(user=self.student_user)

        response = self.client.post(self.url, {"message": "Show my attendance"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["role_context"], "student")
        self.assertEqual(response.data["provider"], "fallback")
        self.assertIn("attendance", response.data["assistant_message"].lower())
        self.assertEqual(AIChat.objects.count(), 1)

        history_response = self.client.get(self.url)
        self.assertEqual(history_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(history_response.data["history"]), 1)
        self.assertEqual(history_response.data["history"][0]["user_message"], "Show my attendance")

    def test_teacher_chat_returns_low_attendance_students(self):
        self.client.force_authenticate(user=self.teacher_user)

        response = self.client.post(self.url, {"message": "Which students have low attendance?"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["role_context"], "teacher")
        self.assertIn("student one", response.data["assistant_message"].lower())

    def test_student_briefing_returns_one_click_sections(self):
        self.client.force_authenticate(user=self.student_user)

        response = self.client.get("/api/ai/briefing/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["role_context"], "student")
        self.assertIn("attendance", response.data["summary"].lower())
        self.assertGreaterEqual(len(response.data["sections"]), 3)
        self.assertEqual(response.data["sections"][0]["title"], "Attendance")
        self.assertEqual(response.data["sections"][0]["action"]["path"], "/student/dashboard")

    def test_teacher_briefing_returns_action_paths(self):
        self.client.force_authenticate(user=self.teacher_user)

        response = self.client.get("/api/ai/briefing/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["role_context"], "teacher")
        paths = [section["action"]["path"] for section in response.data["sections"]]
        self.assertIn("/admin/attendance", paths)
        self.assertIn("/admin/exams", paths)
