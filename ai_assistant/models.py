from django.conf import settings
from django.db import models

from accounts.models import Institution
from core.managers import TenantAwareManager


class AIChat(models.Model):
    objects = TenantAwareManager()
    all_objects = models.Manager()
    tenant_field = "institution"

    ROLE_STUDENT = "student"
    ROLE_TEACHER = "teacher"
    ROLE_ADMIN = "admin"

    ROLE_CHOICES = (
        (ROLE_STUDENT, "Student"),
        (ROLE_TEACHER, "Teacher"),
        (ROLE_ADMIN, "Admin"),
    )

    PROVIDER_OPENAI = "openai"
    PROVIDER_FALLBACK = "fallback"

    PROVIDER_CHOICES = (
        (PROVIDER_OPENAI, "OpenAI"),
        (PROVIDER_FALLBACK, "Fallback"),
    )

    institution = models.ForeignKey(
        Institution,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="ai_chats",
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ai_chats")
    role_context = models.CharField(max_length=20, choices=ROLE_CHOICES)
    message = models.TextField()
    response = models.TextField()
    context_snapshot = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES, default=PROVIDER_FALLBACK)
    model_name = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"AI chat {self.pk} for {self.user}"

