from django.contrib import admin

from .models import AdmissionApplication


@admin.register(AdmissionApplication)
class AdmissionApplicationAdmin(admin.ModelAdmin):
    list_display = ("applicant_name", "program", "academic_year", "status", "institution", "created_at")
    list_filter = ("status", "institution", "academic_year")
    search_fields = ("applicant_name", "email", "phone")
