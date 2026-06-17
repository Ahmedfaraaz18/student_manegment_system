from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from accounts.models import Institution
from accounts.serializers import InstitutionSettingsSerializer

from .models import SubscriptionPlan, TenantDomain, TenantSubscription, TenantUsageSnapshot
from .services import provision_tenant

User = get_user_model()


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = [
            "id",
            "name",
            "code",
            "description",
            "max_students",
            "max_teachers",
            "enabled_features",
            "price_monthly",
            "duration_days",
            "is_active",
        ]


class TenantDomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantDomain
        fields = ["id", "domain", "is_primary", "verified"]


class TenantSubscriptionSerializer(serializers.ModelSerializer):
    plan_name = serializers.CharField(source="plan.name", read_only=True)
    effective_max_students = serializers.IntegerField(read_only=True)
    effective_max_teachers = serializers.IntegerField(read_only=True)
    effective_features = serializers.ListField(read_only=True)

    class Meta:
        model = TenantSubscription
        fields = [
            "id",
            "plan",
            "plan_name",
            "status",
            "starts_at",
            "expires_at",
            "auto_renew",
            "max_students_override",
            "max_teachers_override",
            "feature_overrides",
            "effective_max_students",
            "effective_max_teachers",
            "effective_features",
        ]


class InstitutionSerializer(serializers.ModelSerializer):
    settings = InstitutionSettingsSerializer(read_only=True)
    subscription = TenantSubscriptionSerializer(read_only=True)
    domains = TenantDomainSerializer(many=True, read_only=True)

    class Meta:
        model = Institution
        fields = [
            "id",
            "name",
            "code",
            "institution_type",
            "contact_email",
            "phone",
            "address",
            "is_active",
            "status",
            "created_at",
            "settings",
            "subscription",
            "domains",
        ]


class TenantProvisionSerializer(serializers.Serializer):
    institution_name = serializers.CharField(max_length=200)
    institution_code = serializers.SlugField(max_length=50)
    institution_type = serializers.ChoiceField(choices=Institution.TYPE_CHOICES, default=Institution.COLLEGE)
    contact_email = serializers.EmailField(required=False, allow_blank=True)
    phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    admin_name = serializers.CharField(max_length=150)
    admin_username = serializers.CharField(max_length=150)
    admin_email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)

    def validate_institution_code(self, value):
        if Institution.objects.filter(code=value).exists():
            raise serializers.ValidationError("Institution code already exists.")
        return value

    def validate_admin_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Admin username already exists.")
        return value

    def validate_admin_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Admin email already exists.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        return provision_tenant(
            name=validated_data["institution_name"],
            code=validated_data["institution_code"],
            institution_type=validated_data.get("institution_type", Institution.COLLEGE),
            contact_email=validated_data.get("contact_email", ""),
            phone=validated_data.get("phone", ""),
            address=validated_data.get("address", ""),
            admin_name=validated_data["admin_name"],
            admin_username=validated_data["admin_username"],
            admin_email=validated_data["admin_email"],
            password=validated_data["password"],
            created_by=self.context["request"].user if self.context.get("request") and self.context["request"].user.is_authenticated else None,
        )


class SuperAdminDashboardSerializer(serializers.Serializer):
    total_tenants = serializers.IntegerField()
    active_tenants = serializers.IntegerField()
    suspended_tenants = serializers.IntegerField()
    total_students = serializers.IntegerField()
    total_teachers = serializers.IntegerField()
    active_subscriptions = serializers.IntegerField()
    usage = serializers.ListField()
