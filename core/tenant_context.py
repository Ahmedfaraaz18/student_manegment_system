from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from threading import local
from typing import Iterator, Optional


_state = local()


@dataclass
class TenantContext:
    tenant_id: Optional[int] = None
    user_id: Optional[int] = None
    role: Optional[str] = None
    subdomain: Optional[str] = None
    institution: object | None = None
    enforce_filtering: bool = False

    @property
    def is_super_admin(self) -> bool:
        return self.role == "super_admin"


def get_current_tenant() -> Optional[TenantContext]:
    return getattr(_state, "tenant_context", None)


def set_current_tenant(context: Optional[TenantContext]) -> None:
    _state.tenant_context = context


def clear_current_tenant() -> None:
    if hasattr(_state, "tenant_context"):
        delattr(_state, "tenant_context")


@contextmanager
def tenant_scope_disabled() -> Iterator[None]:
    original = get_current_tenant()
    if original is None:
        yield
        return

    set_current_tenant(
        TenantContext(
            tenant_id=original.tenant_id,
            user_id=original.user_id,
            role=original.role,
            subdomain=original.subdomain,
            institution=original.institution,
            enforce_filtering=False,
        )
    )
    try:
        yield
    finally:
        set_current_tenant(original)
