from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsAdminRole
from accounts.tenancy import filter_queryset_by_institution, get_user_institution

from .models import Subject
from .serializers import SubjectSerializer


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.select_related("institution", "department", "teacher").all()
    serializer_class = SubjectSerializer

    def get_queryset(self):
        queryset = filter_queryset_by_institution(super().get_queryset(), self.request.user)
        user = self.request.user
        if user.is_authenticated and user.role == "teacher" and hasattr(user, "teacher_profile"):
            return queryset.filter(teacher=user.teacher_profile)
        if user.is_authenticated and user.role == "student" and hasattr(user, "student_profile"):
            return queryset.filter(department=user.student_profile.department)
        return queryset

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdminRole()]

    def perform_create(self, serializer):
        serializer.save(institution=get_user_institution(self.request.user))
