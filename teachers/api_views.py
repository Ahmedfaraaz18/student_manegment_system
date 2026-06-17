import csv
from io import StringIO

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.permissions import IsAdminRole
from accounts.tenancy import filter_queryset_by_institution, get_user_institution
from departments.models import Department

from .models import Teacher
from .serializers import TeacherSerializer


def _normalized_row(row):
    normalized = {}
    for key, value in row.items():
        clean_key = (key or "").strip().lower().lstrip("\ufeff")
        normalized[clean_key] = value.strip() if isinstance(value, str) else value
    return normalized


class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.select_related("institution", "department", "user").all()
    serializer_class = TeacherSerializer

    def get_queryset(self):
        return filter_queryset_by_institution(super().get_queryset(), self.request.user)

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
            return Response({"detail": "Only admin can upload teachers."}, status=status.HTTP_403_FORBIDDEN)
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
                    "phone": row.get("phone", ""),
                    "department": department.id,
                },
                context=self.get_serializer_context(),
            )
            serializer.is_valid(raise_exception=True)
            teacher = serializer.save()
            created.append(self.get_serializer(teacher).data)
        return Response(
            {"message": "Teachers uploaded successfully", "teachers_created": len(created), "results": created},
            status=status.HTTP_201_CREATED,
        )
