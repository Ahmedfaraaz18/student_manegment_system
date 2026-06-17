from __future__ import annotations

from datetime import timedelta

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError as DRFValidationError

from accounts.models import Institution, InstitutionSettings, User
from students.models import Student
from teachers.models import Teacher

from .models import SubscriptionPlan, TenantDomain, TenantSubscription, TenantUsageSnapshot


def get_default_plan() -> SubscriptionPlan:
    return SubscriptionPlan.objects.get(code=SubscriptionPlan.FREE)


@transaction.atomic
def provision_tenant(
    *,
    name: str,
    code: str,
    institution_type: str = Institution.COLLEGE,
    contact_email: str = "",
    phone: str = "",
    address: str = "",
    admin_name: str,
    admin_username: str,
    admin_email: str,
    password: str,
    created_by: User | None = None,
) -> dict:
    institution = Institution.objects.create(
        name=name,
        code=code,
        institution_type=institution_type,
        contact_email=contact_email,
        phone=phone,
        address=address,
        status=Institution.ACTIVE,
        created_by=created_by,
    )
    InstitutionSettings.objects.create(
        institution=institution,
        short_name=name,
        support_email=contact_email,
    )
    plan = get_default_plan()
    TenantSubscription.objects.create(
        institution=institution,
        plan=plan,
        status=TenantSubscription.TRIAL,
        expires_at=timezone.now() + timedelta(days=plan.duration_days),
    )
    TenantDomain.objects.create(
        institution=institution,
        domain=f"{code}.app.local",
        is_primary=True,
        verified=False,
    )
    admin_user = User.objects.create_user(
        username=admin_username,
        email=admin_email,
        password=password,
        first_name=admin_name,
        role=User.ADMIN,
        institution=institution,
        is_staff=True,
    )
    TenantUsageSnapshot.objects.create(institution=institution)
    return {"institution": institution, "admin_user": admin_user}


def get_subscription_for_institution(institution: Institution | None) -> TenantSubscription | None:
    if institution is None:
        return None
    return getattr(institution, "subscription", None)


def get_feature_flags(institution: Institution | None) -> list[str]:
    subscription = get_subscription_for_institution(institution)
    if subscription is None:
        return []
    return subscription.effective_features


def enforce_subscription_state(institution: Institution | None) -> None:
    if institution is None:
        return
    if institution.status != Institution.ACTIVE:
        raise PermissionDenied("Tenant is not active.")
    subscription = get_subscription_for_institution(institution)
    if subscription is None:
        raise PermissionDenied("No subscription is configured for this tenant.")
    if subscription.status == TenantSubscription.SUSPENDED:
        raise PermissionDenied("Subscription is suspended.")
    if subscription.is_expired():
        subscription.status = TenantSubscription.EXPIRED
        subscription.save(update_fields=["status", "updated_at"])
        institution.status = Institution.EXPIRED
        institution.save(update_fields=["status", "updated_at"])
        raise PermissionDenied("Subscription has expired.")


def ensure_feature_enabled(institution: Institution | None, feature: str) -> None:
    enforce_subscription_state(institution)
    if feature not in get_feature_flags(institution):
        raise PermissionDenied(f"Feature '{feature}' is not enabled for this tenant.")


def enforce_usage_limit(institution: Institution | None, resource: str) -> None:
    enforce_subscription_state(institution)
    subscription = get_subscription_for_institution(institution)
    if subscription is None:
        raise PermissionDenied("Subscription is required.")

    if resource == "students":
        current = Student.all_objects.filter(institution=institution).count()
        if current >= subscription.effective_max_students:
            raise DRFValidationError({"detail": "Student limit reached for current subscription."})
    elif resource == "teachers":
        current = Teacher.all_objects.filter(institution=institution).count()
        if current >= subscription.effective_max_teachers:
            raise DRFValidationError({"detail": "Teacher limit reached for current subscription."})


def suspend_tenant(institution: Institution) -> Institution:
    institution.status = Institution.SUSPENDED
    institution.is_active = False
    institution.save(update_fields=["status", "is_active", "updated_at"])
    subscription = get_subscription_for_institution(institution)
    if subscription:
        subscription.status = TenantSubscription.SUSPENDED
        subscription.save(update_fields=["status", "updated_at"])
    return institution


def reactivate_tenant(institution: Institution) -> Institution:
    institution.status = Institution.ACTIVE
    institution.is_active = True
    institution.save(update_fields=["status", "is_active", "updated_at"])
    subscription = get_subscription_for_institution(institution)
    if subscription:
        subscription.status = TenantSubscription.ACTIVE
        subscription.save(update_fields=["status", "updated_at"])
    return institution
