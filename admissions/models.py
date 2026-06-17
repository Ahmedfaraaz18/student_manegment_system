from django.db import models

from accounts.models import Institution
from academics.models import AcademicYear, Program, Section
from core.managers import TenantAwareManager


class AdmissionApplication(models.Model):
    objects = TenantAwareManager()
    all_objects = models.Manager()
    tenant_field = "institution"

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

    STATUS_CHOICES = (
        (PENDING, "Pending"),
        (APPROVED, "Approved"),
        (REJECTED, "Rejected"),
    )

    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name="admission_applications")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name="admission_applications")
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name="admission_applications")
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True, blank=True, related_name="admission_applications")
    applicant_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    previous_qualification = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.applicant_name} - {self.program.code}"
