import csv
from io import StringIO, TextIOWrapper

from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from departments.models import Department

from .models import Student
from .serializers import DEFAULT_PASSWORD, StudentSerializer

User = get_user_model()


class StudentListView(ListView):
    model = Student
    template_name = "students/list.html"
    context_object_name = "students"

    def get_queryset(self):
        user = self.request.user

        if not user.is_authenticated:
            return Student.objects.none()

        if user.role == User.SUPER_ADMIN:
            return Student.objects.all()

        institution = getattr(user, "institution", None)
        if institution is None:
            return Student.objects.none()

        return Student.objects.filter(institution=institution)


class StudentCreateView(CreateView):
    model = Student
    fields = ["name", "email", "year", "institution", "department"]
    template_name = "students/form.html"
    success_url = reverse_lazy("student_list")

    def form_valid(self, form):
        email = (form.instance.email or "").strip().lower()
        user, created = User.all_objects.get_or_create(
            username=email,
            defaults={
                "email": form.instance.email,
                "role": User.STUDENT,
                "first_name": form.instance.name,
                "institution": form.instance.institution,
            },
        )
        if created:
            user.set_password(DEFAULT_PASSWORD)
            user.save()
        form.instance.user = user
        response = super().form_valid(form)
        return response


class StudentUpdateView(UpdateView):
    model = Student
    fields = ["name", "email", "year", "institution", "department"]
    template_name = "students/form.html"
    success_url = reverse_lazy("student_list")


class StudentDeleteView(DeleteView):
    model = Student
    template_name = "students/confirm_delete.html"
    success_url = reverse_lazy("student_list")


def _resolve_department(institution, raw_value):
    value = (raw_value or "").strip()
    if not value:
        return None

    if value.isdigit():
        return Department.objects.filter(pk=int(value), institution=institution).first()

    department = Department.objects.filter(institution=institution, name__iexact=value).first()
    if department:
        return department
    return None


def _import_students_from_reader(reader, request):
    created = []
    institution = getattr(request.user, "institution", None)
    if institution is None:
        return created

    for row in reader:
        email = (row.get("email") or "").strip()
        name = (row.get("name") or "").strip()
        if not email or not name:
            continue

        department = _resolve_department(institution, row.get("department"))
        if department is None:
            continue

        serializer = StudentSerializer(
            data={
                "name": name,
                "email": email,
                "year": int(row.get("year") or 1),
                "department": department.id,
            },
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        student = serializer.save()
        created.append(student)
    return created


class BulkStudentUpload(APIView):
    def post(self, request):
        upload = request.FILES.get("file")
        if upload is None:
            return Response({"detail": "CSV file is required."}, status=status.HTTP_400_BAD_REQUEST)

        reader = csv.DictReader(TextIOWrapper(upload.file, encoding="utf-8"))
        created = _import_students_from_reader(reader, request)
        return Response({"message": "Students uploaded successfully", "students_created": len(created)})


@api_view(["POST"])
def bulk_upload_students(request):
    upload = request.FILES.get("file")
    if upload is None:
        return Response({"detail": "CSV file is required."}, status=status.HTTP_400_BAD_REQUEST)

    decoded = upload.read().decode("utf-8")
    reader = csv.DictReader(StringIO(decoded))
    created = _import_students_from_reader(reader, request)
    return Response({"message": "Students uploaded successfully", "students_created": len(created)})
