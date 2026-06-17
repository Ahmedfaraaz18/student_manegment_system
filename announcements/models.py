from django.conf import settings
from django.db import models

from accounts.models import Institution
from core.managers import TenantAwareManager


class Announcement(models.Model):
    objects = TenantAwareManager()
    all_objects = models.Manager()
    tenant_field = "institution"

    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name="announcements", null=True, blank=True)
    title = models.CharField(max_length=200)
    message = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="announcements")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
