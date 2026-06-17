from core.tenant_context import get_current_tenant


def get_user_institution(user):
    if not getattr(user, "is_authenticated", False):
        return None
    tenant_context = get_current_tenant()
    if tenant_context and tenant_context.institution is not None:
        return tenant_context.institution
    institution = getattr(user, "institution", None)
    if institution is not None:
        return institution
    teacher = getattr(user, "teacher_profile", None)
    if teacher is not None:
        return teacher.institution
    student = getattr(user, "student_profile", None)
    if student is not None:
        return student.institution
    return None


def filter_queryset_by_institution(queryset, user, field_name="institution"):
    tenant_context = get_current_tenant()
    if tenant_context and tenant_context.is_super_admin and tenant_context.tenant_id is None:
        return queryset
    if getattr(user, "is_superuser", False) and getattr(user, "institution_id", None) is None:
        return queryset
    institution = get_user_institution(user)
    if institution is None:
        return queryset.none()
    return queryset.filter(**{f"{field_name}_id": institution.id})
