from rest_framework.routers import DefaultRouter

from .api_views import AdmissionApplicationViewSet

router = DefaultRouter()
router.register("", AdmissionApplicationViewSet, basename="admission-application")

urlpatterns = router.urls
