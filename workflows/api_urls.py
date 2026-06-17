from rest_framework.routers import DefaultRouter

from .api_views import ApprovalRequestViewSet

router = DefaultRouter()
router.register("", ApprovalRequestViewSet, basename="approval-request")

urlpatterns = router.urls
