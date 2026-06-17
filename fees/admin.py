from django.contrib import admin

from .models import FeeInvoice, FeePayment, FeeStructure


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ("name", "program", "academic_year", "amount", "institution")
    list_filter = ("institution", "academic_year")


@admin.register(FeeInvoice)
class FeeInvoiceAdmin(admin.ModelAdmin):
    list_display = ("student", "fee_structure", "amount", "amount_paid", "status", "due_date")
    list_filter = ("institution", "status", "due_date")


@admin.register(FeePayment)
class FeePaymentAdmin(admin.ModelAdmin):
    list_display = ("invoice", "amount", "payment_date", "mode")
    list_filter = ("institution", "mode", "payment_date")
