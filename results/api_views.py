from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.permissions import IsAdminOrTeacherRole
from accounts.tenancy import filter_queryset_by_institution, get_user_institution
from students.models import Student
from subjects.models import Subject

from .models import Result
from .serializers import ResultSerializer


class ResultViewSet(viewsets.ModelViewSet):
    queryset = Result.objects.select_related("institution", "student", "subject", "exam").all()
    serializer_class = ResultSerializer

    def get_queryset(self):
        queryset = filter_queryset_by_institution(super().get_queryset(), self.request.user)
        user = self.request.user
        if user.is_authenticated and user.role == "teacher" and hasattr(user, "teacher_profile"):
            return queryset.filter(subject__teacher=user.teacher_profile)
        if user.is_authenticated and user.role == "student" and hasattr(user, "student_profile"):
            return queryset.filter(student=user.student_profile)
        return queryset

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy", "upload_marks"]:
            return [IsAuthenticated(), IsAdminOrTeacherRole()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        institution = get_user_institution(self.request.user)
        subject = Subject.objects.filter(pk=self.request.data.get("subject"), institution=institution).first()
        if subject is None:
            raise PermissionDenied("Subject not found for your institution.")
        user = self.request.user
        if user.role == "teacher" and getattr(user, "teacher_profile", None) != subject.teacher:
            raise PermissionDenied("You can only upload marks for your subjects.")
        serializer.save(institution=institution)

    @action(detail=False, methods=["post"], url_path="upload-marks")
    def upload_marks(self, request):
        results = []
        institution = get_user_institution(request.user)
        for payload in request.data.get("results", []):
            subject = Subject.objects.filter(pk=payload["subject"], institution=institution).first()
            if subject is None:
                return Response({"detail": "Subject not found for your institution."}, status=status.HTTP_404_NOT_FOUND)
            if request.user.role == "teacher" and getattr(request.user, "teacher_profile", None) != subject.teacher:
                return Response({"detail": "You can only upload marks for your subjects."}, status=status.HTTP_403_FORBIDDEN)
            student = Student.objects.filter(pk=payload["student"], institution=institution).first()
            if student is None:
                return Response({"detail": "Student not found for your institution."}, status=status.HTTP_404_NOT_FOUND)
            result, _ = Result.objects.update_or_create(
                institution=institution,
                student=student,
                subject=subject,
                exam_id=payload.get("exam"),
                defaults={"marks": payload["marks"]},
            )
            results.append(ResultSerializer(result).data)
        return Response(results)

    @action(detail=False, methods=["get"], url_path="student-summary")
    def student_summary(self, request):
        student = getattr(request.user, "student_profile", None)
        if student is None and request.query_params.get("student"):
            student = Student.objects.filter(
                pk=request.query_params["student"],
                institution=get_user_institution(request.user),
            ).first()
        if student is None:
            return Response({"detail": "Student context is required."}, status=status.HTTP_400_BAD_REQUEST)
        queryset = self.get_queryset().filter(student=student)
        return Response(ResultSerializer(queryset, many=True).data)
