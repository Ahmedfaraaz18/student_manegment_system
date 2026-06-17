from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsManagementRole
from accounts.tenancy import filter_queryset_by_institution, get_user_institution

from .models import FeeInvoice, FeePayment, FeeStructure
from .serializers import FeeInvoiceSerializer, FeePaymentSerializer, FeeStructureSerializer


class FeeStructureViewSet(viewsets.ModelViewSet):
    queryset = FeeStructure.objects.select_related("academic_year", "program").all()
    serializer_class = FeeStructureSerializer

    def get_queryset(self):
        return filter_queryset_by_institution(super().get_queryset(), self.request.user)

    def get_permissions(self):
        return [IsAuthenticated(), IsManagementRole()]

    def perform_create(self, serializer):
        serializer.save(institution=get_user_institution(self.request.user))


class FeeInvoiceViewSet(viewsets.ModelViewSet):
    queryset = FeeInvoice.objects.select_related("student", "fee_structure").all()
    serializer_class = FeeInvoiceSerializer

    def get_queryset(self):
        return filter_queryset_by_institution(super().get_queryset(), self.request.user)

    def get_permissions(self):
        return [IsAuthenticated(), IsManagementRole()]

    def perform_create(self, serializer):
        serializer.save(institution=get_user_institution(self.request.user))


class FeePaymentViewSet(viewsets.ModelViewSet):
    queryset = FeePayment.objects.select_related("invoice", "invoice__student").all()
    serializer_class = FeePaymentSerializer

    def get_queryset(self):
        return filter_queryset_by_institution(super().get_queryset(), self.request.user)

    def get_permissions(self):
        return [IsAuthenticated(), IsManagementRole()]

    def perform_create(self, serializer):
        serializer.save(institution=get_user_institution(self.request.user))
