from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Result


class ResultListView(ListView):
    model = Result
    template_name = "results/list.html"
    context_object_name = "results"


class ResultCreateView(CreateView):
    model = Result
    fields = ["student", "subject", "exam_type", "marks", "date"]
    template_name = "results/form.html"
    success_url = reverse_lazy("result_list")


class ResultUpdateView(UpdateView):
    model = Result
    fields = ["student", "subject", "exam_type", "marks", "date"]
    template_name = "results/form.html"
    success_url = reverse_lazy("result_list")


class ResultDeleteView(DeleteView):
    model = Result
    template_name = "results/confirm_delete.html"
    success_url = reverse_lazy("result_list")
