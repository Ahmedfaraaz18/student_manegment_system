from django.contrib import admin

from .models import AIChat


@admin.register(AIChat)
class AIChatAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "role_context", "provider", "model_name", "created_at")
    list_filter = ("role_context", "provider", "created_at")
    search_fields = ("user__username", "message", "response")
    readonly_fields = ("created_at", "updated_at")

