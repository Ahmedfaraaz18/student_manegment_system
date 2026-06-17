from rest_framework.routers import DefaultRouter

from .api_views import ExamViewSet

router = DefaultRouter()
router.register("", ExamViewSet, basename="exam")

urlpatterns = router.urls
