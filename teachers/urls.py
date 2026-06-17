from django.urls import path
from .views import (
    TeacherListView,
    TeacherCreateView,
    TeacherUpdateView,
    TeacherDeleteView,
)

urlpatterns = [
    path("", TeacherListView.as_view(), name="teacher_list"),
    path("add/", TeacherCreateView.as_view(), name="teacher_add"),
    path("edit/<int:pk>/", TeacherUpdateView.as_view(), name="teacher_edit"),
    path("delete/<int:pk>/", TeacherDeleteView.as_view(), name="teacher_delete"),
]

