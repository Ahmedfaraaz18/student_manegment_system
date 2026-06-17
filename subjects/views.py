from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Subject


class SubjectListView(ListView):
    model = Subject
    template_name = "subjects/list.html"
    context_object_name = "subjects"


class SubjectCreateView(CreateView):
    model = Subject
    fields = ["name", "institution", "department", "teacher"]
    template_name = "subjects/form.html"
    success_url = reverse_lazy("subject_list")


class SubjectUpdateView(UpdateView):
    model = Subject
    fields = ["name", "institution", "department", "teacher"]
    template_name = "subjects/form.html"
    success_url = reverse_lazy("subject_list")


class SubjectDeleteView(DeleteView):
    model = Subject
    template_name = "subjects/confirm_delete.html"
    success_url = reverse_lazy("subject_list")
