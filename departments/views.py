from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Department


class AcademicUnitListView(ListView):
    model = Department
    template_name = "departments/list.html"
    context_object_name = "academic_units"


class AcademicUnitCreateView(CreateView):
    model = Department
    fields = ["institution", "name"]
    template_name = "departments/form.html"
    success_url = reverse_lazy("academicunit_list")


class AcademicUnitUpdateView(UpdateView):
    model = Department
    fields = ["institution", "name"]
    template_name = "departments/form.html"
    success_url = reverse_lazy("academicunit_list")


class AcademicUnitDeleteView(DeleteView):
    model = Department
    template_name = "departments/confirm_delete.html"
    success_url = reverse_lazy("academicunit_list")

# Create your views here.
