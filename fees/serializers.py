from decimal import Decimal
from datetime import timedelta

from django.db.models import Sum
from django.utils import timezone
from rest_framework import serializers

from accounts.tenancy import get_user_institution

from .models import FeeInvoice, FeePayment, FeeStructure


class FeeStructureSerializer(serializers.ModelSerializer):
    academic_year_name = serializers.CharField(source="academic_year.name", read_only=True)
    program_name = serializers.CharField(source="program.name", read_only=True)

    class Meta:
        model = FeeStructure
        fields = ["id", "name", "amount", "due_days", "academic_year", "academic_year_name", "program", "program_name"]

    def validate(self, attrs):
        institution = get_user_institution(self.context["request"].user)
        academic_year = attrs.get("academic_year") or getattr(self.instance, "academic_year", None)
        program = attrs.get("program") or getattr(self.instance, "program", None)
        if institution is None:
            raise serializers.ValidationError("Institution context is required.")
        if academic_year and academic_year.institution_id != institution.id:
            raise serializers.ValidationError({"academic_year": "Academic year must belong to your institution."})
        if program and program.institution_id != institution.id:
            raise serializers.ValidationError({"program": "Program must belong to your institution."})
        return attrs


class FeeInvoiceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.name", read_only=True)
    fee_structure_name = serializers.CharField(source="fee_structure.name", read_only=True)
    balance = serializers.SerializerMethodField()

    class Meta:
        model = FeeInvoice
        fields = ["id", "student", "student_name", "fee_structure", "fee_structure_name", "amount", "amount_paid", "balance", "due_date", "status", "created_at"]
        read_only_fields = ["amount_paid", "status", "created_at"]
        extra_kwargs = {
            "due_date": {"required": False},
            "amount": {"required": False},
        }

    def get_balance(self, obj):
        return float(obj.amount - obj.amount_paid)

    def validate(self, attrs):
        institution = get_user_institution(self.context["request"].user)
        student = attrs.get("student") or getattr(self.instance, "student", None)
        fee_structure = attrs.get("fee_structure") or getattr(self.instance, "fee_structure", None)
        if institution is None:
            raise serializers.ValidationError("Institution context is required.")
        if student and student.institution_id != institution.id:
            raise serializers.ValidationError({"student": "Student must belong to your institution."})
        if fee_structure and fee_structure.institution_id != institution.id:
            raise serializers.ValidationError({"fee_structure": "Fee structure must belong to your institution."})
        return attrs

    def create(self, validated_data):
        fee_structure = validated_data["fee_structure"]
        validated_data.setdefault("amount", fee_structure.amount)
        validated_data.setdefault("due_date", timezone.now().date() + timedelta(days=fee_structure.due_days))
        return super().create(validated_data)


class FeePaymentSerializer(serializers.ModelSerializer):
    invoice_student_name = serializers.CharField(source="invoice.student.name", read_only=True)

    class Meta:
        model = FeePayment
        fields = ["id", "invoice", "invoice_student_name", "amount", "payment_date", "reference_number", "mode"]

    def validate_invoice(self, invoice):
        institution = get_user_institution(self.context["request"].user)
        if institution and invoice.institution_id != institution.id:
            raise serializers.ValidationError("Invoice must belong to your institution.")
        return invoice

    def create(self, validated_data):
        payment = super().create(validated_data)
        invoice = payment.invoice
        total_paid = invoice.payments.aggregate(total=Sum("amount"))["total"] or Decimal("0")
        invoice.amount_paid = total_paid
        if invoice.amount_paid >= invoice.amount:
            invoice.status = FeeInvoice.PAID
        elif invoice.amount_paid > 0:
            invoice.status = FeeInvoice.PARTIAL
        else:
            invoice.status = FeeInvoice.PENDING
        invoice.save(update_fields=["amount_paid", "status"])
        return payment
