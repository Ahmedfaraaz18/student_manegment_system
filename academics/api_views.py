from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsManagementRole
from accounts.tenancy import filter_queryset_by_institution, get_user_institution

from .models import AcademicYear, Program, Section
from .serializers import AcademicYearSerializer, ProgramSerializer, SectionSerializer


class AcademicYearViewSet(viewsets.ModelViewSet):
    queryset = AcademicYear.objects.all()
    serializer_class = AcademicYearSerializer

    def get_queryset(self):
        return filter_queryset_by_institution(super().get_queryset(), self.request.user)

    def get_permissions(self):
        return [IsAuthenticated(), IsManagementRole()]

    def perform_create(self, serializer):
        institution = get_user_institution(self.request.user)
        if serializer.validated_data.get("is_current"):
            AcademicYear.objects.filter(institution=institution, is_current=True).update(is_current=False)
        serializer.save(institution=institution)

    def perform_update(self, serializer):
        institution = get_user_institution(self.request.user)
        if serializer.validated_data.get("is_current"):
            AcademicYear.objects.filter(institution=institution, is_current=True).exclude(pk=self.get_object().pk).update(is_current=False)
        serializer.save()


class ProgramViewSet(viewsets.ModelViewSet):
    queryset = Program.objects.select_related("department").all()
    serializer_class = ProgramSerializer

    def get_queryset(self):
        return filter_queryset_by_institution(super().get_queryset(), self.request.user)

    def get_permissions(self):
        return [IsAuthenticated(), IsManagementRole()]

    def perform_create(self, serializer):
        serializer.save(institution=get_user_institution(self.request.user))


class SectionViewSet(viewsets.ModelViewSet):
    queryset = Section.objects.select_related("academic_year", "program").all()
    serializer_class = SectionSerializer

    def get_queryset(self):
        return filter_queryset_by_institution(super().get_queryset(), self.request.user)

    def get_permissions(self):
        return [IsAuthenticated(), IsManagementRole()]

    def perform_create(self, serializer):
        serializer.save(institution=get_user_institution(self.request.user))
