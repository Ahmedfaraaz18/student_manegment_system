from django.db import models

from accounts.models import Institution
from core.managers import TenantAwareManager


class Placement(models.Model):
    objects = TenantAwareManager()
    all_objects = models.Manager()
    tenant_field = "institution"

    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name="placements", null=True, blank=True)
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="placements")
    company = models.CharField(max_length=150)
    package = models.DecimalField(max_digits=10, decimal_places=2)
    year = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ["-year", "company"]

    def __str__(self):
        return f"{self.student} - {self.company}"
