from django.urls import path
from .views import (
    AcademicUnitListView,
    AcademicUnitCreateView,
    AcademicUnitUpdateView,
    AcademicUnitDeleteView,
)

urlpatterns = [
    path("", AcademicUnitListView.as_view(), name="academicunit_list"),
    path("add/", AcademicUnitCreateView.as_view(), name="academicunit_add"),
    path("edit/<int:pk>/", AcademicUnitUpdateView.as_view(), name="academicunit_edit"),
    path("delete/<int:pk>/", AcademicUnitDeleteView.as_view(), name="academicunit_delete"),
]
