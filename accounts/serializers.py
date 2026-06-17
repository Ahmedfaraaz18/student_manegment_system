from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from .models import Institution, InstitutionSettings
from tenants.services import provision_tenant

User = get_user_model()


class InstitutionRegistrationSerializer(serializers.Serializer):
    institution_name = serializers.CharField(max_length=200)
    institution_code = serializers.SlugField(max_length=50)
    contact_email = serializers.EmailField(required=False, allow_blank=True)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    admin_name = serializers.CharField(max_length=150)
    admin_username = serializers.CharField(max_length=150)
    admin_email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)

    def validate_institution_code(self, value):
        if Institution.objects.filter(code=value).exists():
            raise serializers.ValidationError("An institution with this code already exists.")
        return value

    def validate_admin_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This admin username is already taken.")
        return value

    def validate_admin_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This admin email is already registered.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        return provision_tenant(
            name=validated_data["institution_name"],
            code=validated_data["institution_code"],
            contact_email=validated_data.get("contact_email", ""),
            phone=validated_data.get("phone", ""),
            address=validated_data.get("address", ""),
            admin_name=validated_data["admin_name"],
            admin_username=validated_data["admin_username"],
            admin_email=validated_data["admin_email"],
            password=validated_data["password"],
        )


class InstitutionSettingsSerializer(serializers.ModelSerializer):
    institution_name = serializers.CharField(source="institution.name", read_only=True)
    institution_code = serializers.CharField(source="institution.code", read_only=True)

    class Meta:
        model = InstitutionSettings
        fields = [
            "institution_name",
            "institution_code",
            "short_name",
            "primary_color",
            "support_email",
            "attendance_threshold",
            "grading_scheme",
            "current_academic_year",
            "logo_url",
        ]
