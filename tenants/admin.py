from django.contrib import admin

from .models import AuditLog, SubscriptionPlan, TenantDomain, TenantSubscription, TenantUsageSnapshot

admin.site.register(SubscriptionPlan)
admin.site.register(TenantSubscription)
admin.site.register(TenantDomain)
admin.site.register(TenantUsageSnapshot)
admin.site.register(AuditLog)

