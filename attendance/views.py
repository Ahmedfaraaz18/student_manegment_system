from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from accounts.permissions import IsTeacher
from .models import Attendance


class AttendanceListView(ListView):
    model = Attendance
    template_name = "attendance/list.html"
    context_object_name = "attendances"


class AttendanceCreateView(CreateView):
    model = Attendance
    fields = ["student", "subject", "date", "status"]
    template_name = "attendance/form.html"
    success_url = reverse_lazy("attendance_list")


class AttendanceUpdateView(UpdateView):
    model = Attendance
    fields = ["student", "subject", "date", "status"]
    template_name = "attendance/form.html"
    success_url = reverse_lazy("attendance_list")


class AttendanceDeleteView(DeleteView):
    model = Attendance
    template_name = "attendance/confirm_delete.html"
    success_url = reverse_lazy("attendance_list")


@api_view(["GET"])
@permission_classes([IsTeacher])
def teacher_attendance_dashboard(request):
    return Response({
        "message": "Welcome Teacher"
    })
