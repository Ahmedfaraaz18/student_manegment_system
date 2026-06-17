from django.db import models

from accounts.models import Institution
from core.managers import TenantAwareManager


class Exam(models.Model):
    objects = TenantAwareManager()
    all_objects = models.Manager()
    tenant_field = "institution"

    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name="exams", null=True, blank=True)
    name = models.CharField(max_length=120)
    date = models.DateField()

    class Meta:
        ordering = ["-date", "name"]
        unique_together = ("institution", "name", "date")

    def __str__(self):
        return self.name
