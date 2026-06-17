from django.db.models import Count, Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import Institution
from accounts.permissions import IsSuperAdminRole
from students.models import Student
from teachers.models import Teacher

from .models import SubscriptionPlan, TenantSubscription, TenantUsageSnapshot
from .serializers import (
    InstitutionSerializer,
    SubscriptionPlanSerializer,
    TenantProvisionSerializer,
    TenantSubscriptionSerializer,
)
from .services import reactivate_tenant, suspend_tenant


class SubscriptionPlanViewSet(viewsets.ModelViewSet):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [IsAuthenticated, IsSuperAdminRole]


class TenantSubscriptionViewSet(viewsets.ModelViewSet):
    queryset = TenantSubscription.objects.select_related("institution", "plan").all()
    serializer_class = TenantSubscriptionSerializer
    permission_classes = [IsAuthenticated, IsSuperAdminRole]


class InstitutionViewSet(viewsets.ModelViewSet):
    queryset = Institution.objects.select_related("subscription", "settings").prefetch_related("domains").all()
    serializer_class = InstitutionSerializer
    permission_classes = [IsAuthenticated, IsSuperAdminRole]

    def create(self, request, *args, **kwargs):
        serializer = TenantProvisionSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        response_serializer = self.get_serializer(result["institution"])
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def suspend(self, request, pk=None):
        institution = self.get_object()
        suspend_tenant(institution)
        return Response(self.get_serializer(institution).data)

    @action(detail=True, methods=["post"])
    def reactivate(self, request, pk=None):
        institution = self.get_object()
        reactivate_tenant(institution)
        return Response(self.get_serializer(institution).data)

    @action(detail=True, methods=["post"])
    def soft_delete(self, request, pk=None):
        institution = self.get_object()
        institution.status = Institution.DELETED
        institution.is_deleted = True
        institution.is_active = False
        institution.save(update_fields=["status", "is_deleted", "is_active", "updated_at"])
        return Response(self.get_serializer(institution).data)


class SuperAdminDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdminRole]

    def get(self, request, *args, **kwargs):
        usage = list(
            TenantUsageSnapshot.objects.select_related("institution")
            .values("institution__name", "student_count", "teacher_count", "active_user_count", "recorded_at")[:10]
        )
        return Response(
            {
                "total_tenants": Institution.objects.count(),
                "active_tenants": Institution.objects.filter(status=Institution.ACTIVE).count(),
                "suspended_tenants": Institution.objects.filter(status=Institution.SUSPENDED).count(),
                "total_students": Student.all_objects.count(),
                "total_teachers": Teacher.all_objects.count(),
                "active_subscriptions": TenantSubscription.objects.filter(
                    Q(status=TenantSubscription.ACTIVE) | Q(status=TenantSubscription.TRIAL)
                ).count(),
                "tenant_breakdown": list(
                    Institution.objects.annotate(
                        student_count=Count("students", distinct=True),
                        teacher_count=Count("teachers", distinct=True),
                    ).values("id", "name", "code", "institution_type", "status", "student_count", "teacher_count")
                ),
                "usage": usage,
            }
        )
