from django.db import models

from accounts.models import Institution
from core.managers import TenantAwareManager


class Result(models.Model):
    objects = TenantAwareManager()
    all_objects = models.Manager()
    tenant_field = "institution"

    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name="results", null=True, blank=True)
    student = models.ForeignKey("students.Student", on_delete=models.CASCADE, related_name="results")
    subject = models.ForeignKey("subjects.Subject", on_delete=models.CASCADE, related_name="results")
    exam = models.ForeignKey("exams.Exam", on_delete=models.SET_NULL, null=True, blank=True, related_name="results")
    marks = models.PositiveIntegerField()

    class Meta:
        unique_together = ("student", "subject", "exam")
        ordering = ["student__name", "subject__name"]

    @property
    def grade(self):
        if self.marks >= 90:
            return "A+"
        if self.marks >= 80:
            return "A"
        if self.marks >= 70:
            return "B"
        if self.marks >= 60:
            return "C"
        if self.marks >= 50:
            return "D"
        return "F"

    def __str__(self):
        return f"{self.student} - {self.subject}"
