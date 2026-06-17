from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from accounts.tenancy import filter_queryset_by_institution, get_user_institution

from .models import ApprovalRequest
from .serializers import ApprovalRequestSerializer


class ApprovalRequestViewSet(viewsets.ModelViewSet):
    queryset = ApprovalRequest.objects.select_related("requested_by").all()
    serializer_class = ApprovalRequestSerializer

    def get_queryset(self):
        queryset = filter_queryset_by_institution(super().get_queryset(), self.request.user)
        if self.request.user.role == "student":
            return queryset.filter(requested_by=self.request.user)
        return queryset

    def get_permissions(self):
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(
            institution=get_user_institution(self.request.user),
            requested_by=self.request.user,
        )

    def perform_update(self, serializer):
        if self.request.user.role not in {"admin", "hod", "exam_officer"}:
            raise PermissionDenied("Only management users can update approval decisions.")
        serializer.save()
