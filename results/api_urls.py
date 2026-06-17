from rest_framework.routers import DefaultRouter

from .api_views import ResultViewSet

router = DefaultRouter()
router.register("", ResultViewSet, basename="result")

urlpatterns = router.urls
