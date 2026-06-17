from django.contrib import admin

from .models import ApprovalRequest


@admin.register(ApprovalRequest)
class ApprovalRequestAdmin(admin.ModelAdmin):
    list_display = ("title", "request_type", "requested_by", "status", "institution", "created_at")
    list_filter = ("institution", "request_type", "status")
    search_fields = ("title", "requested_by__username")
