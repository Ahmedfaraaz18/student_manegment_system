from django.db.models import Avg, Count
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.permissions import IsAdminRole
from accounts.tenancy import filter_queryset_by_institution, get_user_institution

from .models import Placement
from .serializers import PlacementSerializer


class PlacementViewSet(viewsets.ModelViewSet):
    queryset = Placement.objects.select_related("institution", "student").all()
    serializer_class = PlacementSerializer

    def get_queryset(self):
        queryset = filter_queryset_by_institution(super().get_queryset(), self.request.user)
        user = self.request.user
        if user.is_authenticated and user.role == "student" and hasattr(user, "student_profile"):
            return queryset.filter(student=user.student_profile)
        return queryset

    def get_permissions(self):
        if self.action in ["list", "retrieve", "stats"]:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdminRole()]

    def perform_create(self, serializer):
        serializer.save(institution=get_user_institution(self.request.user))

    @action(detail=False, methods=["get"], url_path="stats")
    def stats(self, request):
        queryset = self.get_queryset()
        metrics = queryset.aggregate(total=Count("id"), average_package=Avg("package"))
        by_company = list(queryset.values("company").annotate(count=Count("id")).order_by("-count", "company"))
        return Response({"metrics": metrics, "by_company": by_company})
