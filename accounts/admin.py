from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Institution, InstitutionSettings, User


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "contact_email", "phone", "is_active")
    search_fields = ("name", "code", "contact_email")
    list_filter = ("is_active",)


@admin.register(InstitutionSettings)
class InstitutionSettingsAdmin(admin.ModelAdmin):
    list_display = ("institution", "short_name", "current_academic_year", "attendance_threshold")
    search_fields = ("institution__name", "short_name", "support_email")


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("ERP", {"fields": ("role", "institution")}),)
    list_display = ("username", "email", "role", "institution", "is_staff", "is_active")
    list_filter = ("role", "institution", "is_staff", "is_active")
