from django.urls import path

from .views import DashboardAnalyticsView, StudentDashboardView, TeacherDashboardView

urlpatterns = [
    path("analytics/", DashboardAnalyticsView.as_view()),
    path("teacher/", TeacherDashboardView.as_view()),
    path("student/", StudentDashboardView.as_view()),
]
