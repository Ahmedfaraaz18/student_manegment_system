from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsAdminRole
from accounts.tenancy import filter_queryset_by_institution, get_user_institution

from .models import Exam
from .serializers import ExamSerializer


class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer

    def get_queryset(self):
        return filter_queryset_by_institution(super().get_queryset(), self.request.user)

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdminRole()]

    def perform_create(self, serializer):
        serializer.save(institution=get_user_institution(self.request.user))
