from __future__ import annotations

from typing import Optional

from django.apps import apps
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError

from .tenant_context import TenantContext, clear_current_tenant, set_current_tenant


class TenantContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        set_current_tenant(self._build_context(request))
        try:
            response = self.get_response(request)
        finally:
            clear_current_tenant()
        return response

    def _build_context(self, request) -> TenantContext:
        Institution = apps.get_model("accounts", "Institution")
        token_payload = self._parse_bearer_token(request)
        tenant_id = token_payload.get("tenant_id") if token_payload else None
        role = token_payload.get("role") if token_payload else None
        user_id = token_payload.get("user_id") if token_payload else None
        subdomain = self._extract_subdomain(request.get_host())
        institution = None

        if tenant_id:
            institution = Institution.objects.filter(pk=tenant_id).first()
        elif subdomain:
            institution = Institution.objects.filter(code=subdomain).first()
            if institution:
                tenant_id = institution.id

        context = TenantContext(
            tenant_id=tenant_id,
            user_id=user_id,
            role=role,
            subdomain=subdomain,
            institution=institution,
            enforce_filtering=bool(tenant_id or role == "super_admin"),
        )
        request.tenant = institution
        request.tenant_id = tenant_id
        request.tenant_role = role
        request.tenant_subdomain = subdomain
        return context

    def _parse_bearer_token(self, request) -> dict:
        header = request.META.get("HTTP_AUTHORIZATION", "")
        if not header.startswith("Bearer "):
            return {}
        token = header.split(" ", 1)[1].strip()
        if not token:
            return {}
        try:
            return AccessToken(token).payload
        except TokenError:
            return {}

    def _extract_subdomain(self, host: str) -> Optional[str]:
        clean_host = host.split(":")[0].lower()
        if clean_host in {"localhost", "127.0.0.1"}:
            return None
        parts = clean_host.split(".")
        if len(parts) < 3:
            return None
        return parts[0]


class AuditLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        self._capture(request, response)
        return response

    def _capture(self, request, response) -> None:
        if request.method not in {"POST", "PUT", "PATCH", "DELETE"}:
            return
        if not getattr(request, "user", None) or not request.user.is_authenticated:
            return
        AuditLog = apps.get_model("tenants", "AuditLog")
        AuditLog.objects.create(
            institution=getattr(request, "tenant", None) or getattr(request.user, "institution", None),
            actor=request.user,
            action=f"{request.method} {request.path}",
            resource_type="http_request",
            resource_id="",
            metadata={
                "status_code": response.status_code,
                "query_params": dict(request.GET),
            },
            ip_address=request.META.get("REMOTE_ADDR", ""),
        )
