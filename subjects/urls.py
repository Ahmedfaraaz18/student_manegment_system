from django.urls import path
from .views import (
    SubjectListView,
    SubjectCreateView,
    SubjectUpdateView,
    SubjectDeleteView,
)

urlpatterns = [
    path("", SubjectListView.as_view(), name="subject_list"),
    path("add/", SubjectCreateView.as_view(), name="subject_add"),
    path("edit/<int:pk>/", SubjectUpdateView.as_view(), name="subject_edit"),
    path("delete/<int:pk>/", SubjectDeleteView.as_view(), name="subject_delete"),
]
