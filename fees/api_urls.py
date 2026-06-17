from rest_framework.routers import DefaultRouter

from .api_views import FeeInvoiceViewSet, FeePaymentViewSet, FeeStructureViewSet

router = DefaultRouter()
router.register("structures", FeeStructureViewSet, basename="fee-structure")
router.register("invoices", FeeInvoiceViewSet, basename="fee-invoice")
router.register("payments", FeePaymentViewSet, basename="fee-payment")

urlpatterns = router.urls
