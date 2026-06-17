from rest_framework.routers import DefaultRouter

from .api_views import TeacherViewSet

router = DefaultRouter()
router.register("", TeacherViewSet, basename="teacher")

urlpatterns = router.urls
