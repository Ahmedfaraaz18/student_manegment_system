from django.db.models import Count, Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.permissions import IsAdminOrTeacherRole
from accounts.tenancy import filter_queryset_by_institution, get_user_institution
from students.models import Student
from subjects.models import Subject

from .models import Attendance
from .serializers import AttendanceBulkSerializer, AttendanceSerializer


class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.select_related("institution", "student", "subject").all()
    serializer_class = AttendanceSerializer

    def get_queryset(self):
        queryset = filter_queryset_by_institution(super().get_queryset(), self.request.user)
        user = self.request.user
        if user.is_authenticated and user.role == "teacher" and hasattr(user, "teacher_profile"):
            return queryset.filter(subject__teacher=user.teacher_profile)
        if user.is_authenticated and user.role == "student" and hasattr(user, "student_profile"):
            return queryset.filter(student=user.student_profile)
        return queryset

    def get_permissions(self):
        if self.action in ["bulk_mark", "create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsAdminOrTeacherRole()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(institution=get_user_institution(self.request.user))

    @action(detail=False, methods=["post"], url_path="mark")
    def bulk_mark(self, request):
        serializer = AttendanceBulkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        institution = get_user_institution(request.user)
        subject = Subject.objects.filter(pk=serializer.validated_data["subject"], institution=institution).first()
        if subject is None:
            return Response({"detail": "Subject not found for your institution."}, status=status.HTTP_404_NOT_FOUND)
        user = request.user
        if user.role == "teacher" and getattr(user, "teacher_profile", None) != subject.teacher:
            return Response({"detail": "You can only mark attendance for your subjects."}, status=status.HTTP_403_FORBIDDEN)

        created = []
        for record in serializer.validated_data["records"]:
            student = Student.objects.filter(pk=record["student"], institution=institution).first()
            if student is None:
                return Response({"detail": "One or more students do not belong to your institution."}, status=status.HTTP_400_BAD_REQUEST)
            attendance, _ = Attendance.objects.update_or_create(
                student=student,
                institution=institution,
                subject=subject,
                date=serializer.validated_data["date"],
                defaults={"status": record["status"]},
            )
            created.append(AttendanceSerializer(attendance).data)
        return Response(created)

    @action(detail=False, methods=["get"], url_path="summary")
    def summary(self, request):
        student = getattr(request.user, "student_profile", None)
        if student is None and request.query_params.get("student"):
            student = Student.objects.filter(
                pk=request.query_params["student"],
                institution=get_user_institution(request.user),
            ).first()
        if student is None:
            return Response({"detail": "Student context is required."}, status=status.HTTP_400_BAD_REQUEST)

        totals = self.get_queryset().filter(student=student).aggregate(
            total=Count("id"),
            present=Count("id", filter=Q(status="Present")),
        )
        total = totals["total"] or 0
        present = totals["present"] or 0
        percentage = round((present / total) * 100, 2) if total else 0
        history = AttendanceSerializer(self.get_queryset().filter(student=student), many=True).data
        return Response({"attendance_percentage": percentage, "history": history})
