from django.conf import settings
from django.db import models

from accounts.models import Institution
from core.managers import TenantAwareManager


class ApprovalRequest(models.Model):
    objects = TenantAwareManager()
    all_objects = models.Manager()
    tenant_field = "institution"

    LEAVE = "leave"
    BONAFIDE = "bonafide"
    DOCUMENT = "document"

    TYPE_CHOICES = (
        (LEAVE, "Leave"),
        (BONAFIDE, "Bonafide"),
        (DOCUMENT, "Document"),
    )

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

    STATUS_CHOICES = (
        (PENDING, "Pending"),
        (APPROVED, "Approved"),
        (REJECTED, "Rejected"),
    )

    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name="approval_requests")
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="approval_requests")
    request_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    decision_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
