from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsManagementRole
from accounts.tenancy import filter_queryset_by_institution, get_user_institution

from .models import AdmissionApplication
from .serializers import AdmissionApplicationSerializer


class AdmissionApplicationViewSet(viewsets.ModelViewSet):
    queryset = AdmissionApplication.objects.select_related("academic_year", "program", "section").all()
    serializer_class = AdmissionApplicationSerializer

    def get_queryset(self):
        return filter_queryset_by_institution(super().get_queryset(), self.request.user)

    def get_permissions(self):
        return [IsAuthenticated(), IsManagementRole()]

    def perform_create(self, serializer):
        serializer.save(institution=get_user_institution(self.request.user))
