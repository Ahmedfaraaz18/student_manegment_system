from django.urls import path
from .views import (
    StudentListView,
    StudentCreateView,
    StudentUpdateView,
    StudentDeleteView,
    BulkStudentUpload,
)

urlpatterns = [
    path("", StudentListView.as_view(), name="student_list"),
    path("add/", StudentCreateView.as_view(), name="student_add"),
    path("edit/<int:pk>/", StudentUpdateView.as_view(), name="student_edit"),
    path("delete/<int:pk>/", StudentDeleteView.as_view(), name="student_delete"),
    path("bulk-upload/", BulkStudentUpload.as_view()),
]
