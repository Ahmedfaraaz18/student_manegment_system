from django.db import models

from .tenant_context import get_current_tenant


def apply_tenant_filter(queryset: models.QuerySet, model: type[models.Model]) -> models.QuerySet:
    context = get_current_tenant()
    if context is None or not context.enforce_filtering:
        return queryset

    tenant_field = getattr(model, "tenant_field", "institution")
    if not any(field.name == tenant_field for field in model._meta.fields):
        return queryset

    if context.is_super_admin and context.tenant_id is None:
        return queryset

    if context.tenant_id is None:
        return queryset.none()

    return queryset.filter(**{f"{tenant_field}_id": context.tenant_id})


class TenantAwareManager(models.Manager):
    def get_queryset(self):
        return apply_tenant_filter(super().get_queryset(), self.model)

