from django.conf import settings
from django.db import models

from accounts.models import Institution
from core.managers import TenantAwareManager


class Student(models.Model):
    objects = TenantAwareManager()
    all_objects = models.Manager()
    tenant_field = "institution"

    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name="students", null=True, blank=True)
    name = models.CharField(max_length=120)
    email = models.EmailField(unique=True)
    year = models.PositiveSmallIntegerField()
    department = models.ForeignKey("departments.Department", on_delete=models.CASCADE, related_name="students")
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="student_profile",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
