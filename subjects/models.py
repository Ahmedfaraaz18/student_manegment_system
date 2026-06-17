from django.db import models

from accounts.models import Institution
from core.managers import TenantAwareManager


class Subject(models.Model):
    objects = TenantAwareManager()
    all_objects = models.Manager()
    tenant_field = "institution"

    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name="subjects", null=True, blank=True)
    name = models.CharField(max_length=120)
    department = models.ForeignKey("departments.Department", on_delete=models.CASCADE, related_name="subjects")
    teacher = models.ForeignKey("teachers.Teacher", on_delete=models.CASCADE, related_name="subjects")

    class Meta:
        ordering = ["name"]
        unique_together = ("institution", "name", "department")

    def __str__(self):
        return self.name
