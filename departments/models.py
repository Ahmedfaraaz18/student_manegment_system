from django.db import models

from accounts.models import Institution
from core.managers import TenantAwareManager


class Department(models.Model):
    objects = TenantAwareManager()
    all_objects = models.Manager()
    tenant_field = "institution"

    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name="departments", null=True, blank=True)
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ["name"]
        unique_together = ("institution", "name")

    def __str__(self):
        return self.name
