import csv
from io import StringIO

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.permissions import IsAdminRole
from accounts.tenancy import filter_queryset_by_institution, get_user_institution
from departments.models import Department

from .models import Student
from .serializers import StudentSerializer


def _normalized_row(row):
    normalized = {}
    for key, value in row.items():
        clean_key = (key or "").strip().lower().lstrip("\ufeff")
        normalized[clean_key] = value.strip() if isinstance(value, str) else value
    return normalized


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.select_related("institution", "department", "user").all()
    serializer_class = StudentSerializer

    def get_queryset(self):
        queryset = filter_queryset_by_institution(super().get_queryset(), self.request.user)
        user = self.request.user
        if user.is_authenticated and user.role == "teacher" and hasattr(user, "teacher_profile"):
            return queryset.filter(department=user.teacher_profile.department)
        if user.is_authenticated and user.role == "student" and hasattr(user, "student_profile"):
            return queryset.filter(pk=user.student_profile.pk)
        return queryset

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdminRole()]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    @action(detail=False, methods=["post"], url_path="upload")
    def upload(self, request):
        if request.user.role != "admin":
            return Response({"detail": "Only admin can upload students."}, status=status.HTTP_403_FORBIDDEN)
        file_obj = request.FILES.get("file")
        if not file_obj:
            return Response({"detail": "CSV file is required."}, status=status.HTTP_400_BAD_REQUEST)

        decoded = file_obj.read().decode("utf-8")
        reader = csv.DictReader(StringIO(decoded))
        created = []
        institution = get_user_institution(request.user)
        for raw_row in reader:
            row = _normalized_row(raw_row)
            department_name = row.get("department", "")
            name = row.get("name", "")
            email = row.get("email", "")

            if not department_name:
                return Response(
                    {"detail": "CSV must include a 'department' column."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if not name or not email:
                return Response(
                    {"detail": "Each CSV row must include both 'name' and 'email'."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            department, _ = Department.objects.get_or_create(
                institution=institution,
                name=department_name,
            )
            serializer = self.get_serializer(
                data={
                    "name": name,
                    "email": email,
                    "year": int(row.get("year") or 1),
                    "department": department.id,
                },
                context=self.get_serializer_context(),
            )
            serializer.is_valid(raise_exception=True)
            student = serializer.save()
            created.append(self.get_serializer(student).data)
        return Response(
            {"message": "Students uploaded successfully", "students_created": len(created), "results": created},
            status=status.HTTP_201_CREATED,
        )
