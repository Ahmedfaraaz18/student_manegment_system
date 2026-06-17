from rest_framework.routers import DefaultRouter

from .api_views import SubjectViewSet

router = DefaultRouter()
router.register("", SubjectViewSet, basename="subject")

urlpatterns = router.urls
