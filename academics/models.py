from django.db import models

from accounts.models import Institution
from core.managers import TenantAwareManager
from departments.models import Department


class AcademicYear(models.Model):
    objects = TenantAwareManager()
    all_objects = models.Manager()
    tenant_field = "institution"

    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name="academic_years")
    name = models.CharField(max_length=20)
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)

    class Meta:
        ordering = ["-start_date"]
        unique_together = ("institution", "name")

    def __str__(self):
        return self.name


class Program(models.Model):
    objects = TenantAwareManager()
    all_objects = models.Manager()
    tenant_field = "institution"

    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name="programs")
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="programs")
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=20)
    duration_years = models.PositiveSmallIntegerField(default=4)

    class Meta:
        ordering = ["name"]
        unique_together = ("institution", "code")

    def __str__(self):
        return f"{self.name} ({self.code})"


class Section(models.Model):
    objects = TenantAwareManager()
    all_objects = models.Manager()
    tenant_field = "institution"

    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name="sections")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name="sections")
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name="sections")
    name = models.CharField(max_length=20)
    semester = models.PositiveSmallIntegerField()
    capacity = models.PositiveIntegerField(default=60)

    class Meta:
        ordering = ["program__name", "semester", "name"]
        unique_together = ("institution", "academic_year", "program", "name", "semester")

    def __str__(self):
        return f"{self.program.code} Sem {self.semester} - {self.name}"
