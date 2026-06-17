from django.conf import settings
from django.db import models
from django.utils import timezone


class SubscriptionPlan(models.Model):
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"

    PLAN_CHOICES = (
        (FREE, "Free"),
        (BASIC, "Basic"),
        (PREMIUM, "Premium"),
    )

    name = models.CharField(max_length=50, choices=PLAN_CHOICES, unique=True)
    code = models.SlugField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    max_students = models.PositiveIntegerField(default=100)
    max_teachers = models.PositiveIntegerField(default=20)
    enabled_features = models.JSONField(default=list, blank=True)
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    duration_days = models.PositiveIntegerField(default=30)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["price_monthly", "name"]

    def __str__(self):
        return self.get_name_display()


class TenantSubscription(models.Model):
    TRIAL = "trial"
    ACTIVE = "active"
    EXPIRED = "expired"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"

    STATUS_CHOICES = (
        (TRIAL, "Trial"),
        (ACTIVE, "Active"),
        (EXPIRED, "Expired"),
        (SUSPENDED, "Suspended"),
        (CANCELLED, "Cancelled"),
    )

    institution = models.OneToOneField(
        "accounts.Institution",
        on_delete=models.CASCADE,
        related_name="subscription",
    )
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT, related_name="subscriptions")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=TRIAL)
    starts_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()
    auto_renew = models.BooleanField(default=False)
    max_students_override = models.PositiveIntegerField(null=True, blank=True)
    max_teachers_override = models.PositiveIntegerField(null=True, blank=True)
    feature_overrides = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    @property
    def effective_max_students(self) -> int:
        return self.max_students_override or self.plan.max_students

    @property
    def effective_max_teachers(self) -> int:
        return self.max_teachers_override or self.plan.max_teachers

    @property
    def effective_features(self) -> list[str]:
        features = set(self.plan.enabled_features)
        for feature, enabled in self.feature_overrides.items():
            if enabled:
                features.add(feature)
            else:
                features.discard(feature)
        return sorted(features)

    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at

    def __str__(self):
        return f"{self.institution.name} - {self.plan.name}"


class TenantDomain(models.Model):
    institution = models.ForeignKey(
        "accounts.Institution",
        on_delete=models.CASCADE,
        related_name="domains",
    )
    domain = models.CharField(max_length=255, unique=True)
    is_primary = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_primary", "domain"]

    def __str__(self):
        return self.domain


class TenantUsageSnapshot(models.Model):
    institution = models.ForeignKey(
        "accounts.Institution",
        on_delete=models.CASCADE,
        related_name="usage_snapshots",
    )
    recorded_at = models.DateTimeField(auto_now_add=True)
    student_count = models.PositiveIntegerField(default=0)
    teacher_count = models.PositiveIntegerField(default=0)
    active_user_count = models.PositiveIntegerField(default=0)
    storage_mb = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-recorded_at"]


class AuditLog(models.Model):
    institution = models.ForeignKey(
        "accounts.Institution",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=200)
    resource_type = models.CharField(max_length=100)
    resource_id = models.CharField(max_length=100, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

