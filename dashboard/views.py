from django.db.models import Count
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from academics.models import AcademicYear, Program, Section
from admissions.models import AdmissionApplication
from accounts.tenancy import get_user_institution
from announcements.models import Announcement
from attendance.models import Attendance
from departments.models import Department
from fees.models import FeeInvoice
from placements.models import Placement
from results.models import Result
from students.models import Student
from subjects.models import Subject
from teachers.models import Teacher
from tenants.services import ensure_feature_enabled, get_subscription_for_institution


class DashboardAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        institution = get_user_institution(request.user)
        if institution is None:
            return Response(
                {
                    "totals": {
                        "students": 0,
                    "teachers": 0,
                    "departments": 0,
                    "programs": 0,
                    "sections": 0,
                    "subjects": 0,
                    "admissions": 0,
                    "pending_fees": 0,
                    "attendance_records": 0,
                    "results": 0,
                },
                    "placement_statistics": {"total_placements": 0, "companies": []},
                }
            )
        ensure_feature_enabled(institution, "analytics")
        subscription = get_subscription_for_institution(institution)
        placements = Placement.objects.filter(institution=institution)
        placement_stats = {
            "total_placements": placements.count(),
            "companies": list(
                placements.values("company").annotate(count=Count("id")).order_by("-count", "company")[:5]
            ),
        }
        return Response(
            {
                "totals": {
                    "students": Student.objects.filter(institution=institution).count(),
                    "teachers": Teacher.objects.filter(institution=institution).count(),
                    "departments": Department.objects.filter(institution=institution).count(),
                    "programs": Program.objects.filter(institution=institution).count(),
                    "sections": Section.objects.filter(institution=institution).count(),
                    "subjects": Subject.objects.filter(institution=institution).count(),
                    "admissions": AdmissionApplication.objects.filter(institution=institution).count(),
                    "pending_fees": FeeInvoice.objects.filter(institution=institution).exclude(status=FeeInvoice.PAID).count(),
                    "attendance_records": Attendance.objects.filter(institution=institution).count(),
                    "results": Result.objects.filter(institution=institution).count(),
                },
                "academic_overview": {
                    "current_year": AcademicYear.objects.filter(institution=institution, is_current=True)
                    .values_list("name", flat=True)
                    .first(),
                    "programs": Program.objects.filter(institution=institution).count(),
                    "sections": Section.objects.filter(institution=institution).count(),
                },
                "placement_statistics": placement_stats,
                "subscription": {
                    "plan": getattr(getattr(subscription, "plan", None), "name", None),
                    "status": getattr(subscription, "status", None),
                    "expires_at": getattr(subscription, "expires_at", None),
                    "features": subscription.effective_features if subscription else [],
                    "limits": {
                        "max_students": subscription.effective_max_students if subscription else None,
                        "max_teachers": subscription.effective_max_teachers if subscription else None,
                    },
                },
            }
        )


class TeacherDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        teacher = getattr(request.user, "teacher_profile", None)
        if teacher is None:
            return Response({"subjects": [], "students": [], "recent_results": []})
        subjects = list(teacher.subjects.select_related("department").values("id", "name", "department__name"))
        students = list(teacher.department.students.values("id", "name", "email", "year"))
        recent_results = list(
            Result.objects.filter(subject__teacher=teacher)
            .select_related("student", "subject", "exam")
            .values("id", "student__name", "subject__name", "marks", "exam__name")[:10]
        )
        return Response({"subjects": subjects, "students": students, "recent_results": recent_results})


class StudentDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        student = getattr(request.user, "student_profile", None)
        if student is None:
            return Response({"attendance_percentage": 0, "results": [], "announcements": []})
        total_attendance = student.attendance_records.count()
        present = student.attendance_records.filter(status="Present").count()
        percentage = round((present / total_attendance) * 100, 2) if total_attendance else 0
        results = [
            {
                "subject": result.subject.name,
                "exam": result.exam.name if result.exam else "General",
                "marks": result.marks,
                "grade": result.grade,
            }
            for result in student.results.select_related("subject", "exam")
        ]
        announcements = list(
            Announcement.objects.filter(institution=student.institution).values("id", "title", "message", "created_at")[:10]
        )
        return Response(
            {
                "attendance_percentage": percentage,
                "results": results,
                "announcements": announcements,
            }
        )
