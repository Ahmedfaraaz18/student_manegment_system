from rest_framework.routers import DefaultRouter

from .api_views import AcademicYearViewSet, ProgramViewSet, SectionViewSet

router = DefaultRouter()
router.register("academic-years", AcademicYearViewSet, basename="academic-year")
router.register("programs", ProgramViewSet, basename="program")
router.register("sections", SectionViewSet, basename="section")

urlpatterns = router.urls
