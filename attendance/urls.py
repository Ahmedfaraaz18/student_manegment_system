from django.urls import path
from .views import (
    AttendanceListView,
    AttendanceCreateView,
    AttendanceUpdateView,
    AttendanceDeleteView,
    teacher_attendance_dashboard,
)

urlpatterns = [
    path("", AttendanceListView.as_view(), name="attendance_list"),
    path("teacher-dashboard/", teacher_attendance_dashboard, name="teacher_attendance_dashboard"),
    path("add/", AttendanceCreateView.as_view(), name="attendance_add"),
    path("edit/<int:pk>/", AttendanceUpdateView.as_view(), name="attendance_edit"),
    path("delete/<int:pk>/", AttendanceDeleteView.as_view(), name="attendance_delete"),
]
