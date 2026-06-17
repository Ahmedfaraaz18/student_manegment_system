from datetime import timedelta

from django.db import connection
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.utils import timezone

from accounts.models import Institution

from .models import SubscriptionPlan
from .models import TenantSubscription, TenantUsageSnapshot


@receiver(post_migrate)
def seed_subscription_plans(sender, **kwargs):
    if sender.name != "tenants":
        return
    existing_tables = set(connection.introspection.table_names())
    required_tables = {
        SubscriptionPlan._meta.db_table,
        TenantSubscription._meta.db_table,
        TenantUsageSnapshot._meta.db_table,
    }
    if not required_tables.issubset(existing_tables):
        return

    plans = [
        {
            "name": SubscriptionPlan.FREE,
            "code": "free",
            "description": "Starter plan for evaluation and demo tenants.",
            "max_students": 100,
            "max_teachers": 20,
            "enabled_features": ["core_erp"],
            "price_monthly": 0,
            "duration_days": 30,
        },
        {
            "name": SubscriptionPlan.BASIC,
            "code": "basic",
            "description": "Operational plan for growing institutions.",
            "max_students": 1000,
            "max_teachers": 200,
            "enabled_features": ["core_erp", "reports", "fees"],
            "price_monthly": 99,
            "duration_days": 30,
        },
        {
            "name": SubscriptionPlan.PREMIUM,
            "code": "premium",
            "description": "Full analytics and automation suite.",
            "max_students": 10000,
            "max_teachers": 2000,
            "enabled_features": ["core_erp", "reports", "fees", "analytics", "branding", "notifications"],
            "price_monthly": 299,
            "duration_days": 30,
        },
    ]
    for plan in plans:
        SubscriptionPlan.objects.update_or_create(code=plan["code"], defaults=plan)

    default_plan = SubscriptionPlan.objects.get(code=SubscriptionPlan.FREE)
    for institution in Institution.objects.filter(is_deleted=False):
        TenantSubscription.objects.get_or_create(
            institution=institution,
            defaults={
                "plan": default_plan,
                "status": TenantSubscription.TRIAL,
                "expires_at": timezone.now() + timedelta(days=default_plan.duration_days),
            },
        )
        TenantUsageSnapshot.objects.get_or_create(institution=institution)
