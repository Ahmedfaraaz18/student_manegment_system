from django.contrib import admin

from .models import AcademicYear, Program, Section


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ("name", "institution", "start_date", "end_date", "is_current")
    list_filter = ("institution", "is_current")


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "department", "institution", "duration_years")
    list_filter = ("institution", "department")
    search_fields = ("name", "code")


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("name", "program", "semester", "academic_year", "capacity", "institution")
    list_filter = ("institution", "semester", "academic_year")
