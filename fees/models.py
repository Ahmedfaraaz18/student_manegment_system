from django.db import models

from accounts.models import Institution
from academics.models import AcademicYear, Program
from core.managers import TenantAwareManager
from students.models import Student


class FeeStructure(models.Model):
    objects = TenantAwareManager()
    all_objects = models.Manager()
    tenant_field = "institution"

    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name="fee_structures")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name="fee_structures")
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name="fee_structures")
    name = models.CharField(max_length=120)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_days = models.PositiveIntegerField(default=30)

    class Meta:
        ordering = ["program__name", "name"]
        unique_together = ("institution", "academic_year", "program", "name")

    def __str__(self):
        return self.name


class FeeInvoice(models.Model):
    objects = TenantAwareManager()
    all_objects = models.Manager()
    tenant_field = "institution"

    PENDING = "pending"
    PARTIAL = "partial"
    PAID = "paid"

    STATUS_CHOICES = (
        (PENDING, "Pending"),
        (PARTIAL, "Partial"),
        (PAID, "Paid"),
    )

    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name="fee_invoices")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="fee_invoices")
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE, related_name="invoices")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["due_date", "-created_at"]

    def __str__(self):
        return f"{self.student.name} - {self.fee_structure.name}"


class FeePayment(models.Model):
    objects = TenantAwareManager()
    all_objects = models.Manager()
    tenant_field = "institution"

    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name="fee_payments")
    invoice = models.ForeignKey(FeeInvoice, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    reference_number = models.CharField(max_length=50, blank=True)
    mode = models.CharField(max_length=30, default="cash")

    class Meta:
        ordering = ["-payment_date", "-id"]

    def __str__(self):
        return f"{self.invoice} - {self.amount}"
