from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path

from accounts.views import LoginView


def root_view(_request):
    return JsonResponse(
        {
            "status": "ok",
            "service": "student_management_system",
            "login_url": "/api/login/",
        }
    )

urlpatterns = [
    path("", root_view),
    path("health/", root_view),
    path("admin/", admin.site.urls),
    path("api/login/", LoginView.as_view()),
    path("api/ai/", include("ai_assistant.api_urls")),
    path("api/accounts/", include("accounts.urls")),
    path("api/academics/", include("academics.api_urls")),
    path("api/admissions/", include("admissions.api_urls")),
    path("api/dashboard/", include("dashboard.urls")),
    path("api/announcements/", include("announcements.api_urls")),
    path("api/departments/", include("departments.api_urls")),
    path("api/teachers/", include("teachers.api_urls")),
    path("api/students/", include("students.api_urls")),
    path("api/subjects/", include("subjects.api_urls")),
    path("api/tenants/", include("tenants.api_urls")),
    path("api/attendance/", include("attendance.api_urls")),
    path("api/exams/", include("exams.api_urls")),
    path("api/fees/", include("fees.api_urls")),
    path("api/results/", include("results.api_urls")),
    path("api/placements/", include("placements.api_urls")),
    path("api/workflows/", include("workflows.api_urls")),
]
