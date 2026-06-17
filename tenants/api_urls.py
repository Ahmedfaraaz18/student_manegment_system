from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .api_views import InstitutionViewSet, SubscriptionPlanViewSet, SuperAdminDashboardView, TenantSubscriptionViewSet

router = DefaultRouter()
router.register("institutions", InstitutionViewSet, basename="institution")
router.register("plans", SubscriptionPlanViewSet, basename="subscription-plan")
router.register("subscriptions", TenantSubscriptionViewSet, basename="tenant-subscription")

urlpatterns = [
    path("dashboard/", SuperAdminDashboardView.as_view()),
    path("", include(router.urls)),
]

