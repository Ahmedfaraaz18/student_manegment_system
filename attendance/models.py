from django.db import models

from accounts.models import Institution
from core.managers import TenantAwareManager


class Attendance(models.Model):
    objects = TenantAwareManager()
    all_objects = models.Manager()
    tenant_field = "institution"

    PRESENT = "Present"
    ABSENT = "Absent"
    STATUS_CHOICES = ((PRESENT, "Present"), (ABSENT, "Absent"))

    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name="attendance_records", null=True, blank=True)
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="attendance_records")
    subject = models.ForeignKey("subjects.Subject", on_delete=models.CASCADE, related_name="attendance_records")
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    class Meta:
        unique_together = ("student", "subject", "date")
        ordering = ["-date"]

    def __str__(self):
        return f"{self.student} - {self.subject} - {self.date}"
