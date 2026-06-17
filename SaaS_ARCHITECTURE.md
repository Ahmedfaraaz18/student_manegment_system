fr# Multi-Tenant SaaS Architecture

## Backend Architecture

- `core/tenant_context.py`
  Provides request-scoped tenant context using thread-local storage.
- `core/middleware.py`
  Extracts `tenant_id`, `role`, and `user_id` from JWT, resolves subdomains, attaches tenant context to the request, and writes audit logs for mutating requests.
- `core/managers.py`
  Implements automatic tenant-aware queryset filtering.
- `tenants/`
  Contains subscription plans, tenant subscriptions, tenant domains, usage snapshots, audit logs, and super-admin APIs.
- Existing domain apps remain as functional modules:
  `students`, `teachers`, `subjects`, `departments`, `academics`, `admissions`, `fees`, `attendance`, `announcements`, `exams`, `results`, `placements`, `workflows`.

## Tenant Isolation

- JWT includes:
  - `user_id`
  - `role`
  - `tenant_id`
- `TenantContextMiddleware` reads those claims and sets:
  - `request.tenant`
  - `request.tenant_id`
  - `request.tenant_role`
- Tenant-owned models use `TenantAwareManager`, which automatically applies `institution_id = current_tenant_id` unless the caller is `super_admin`.

## Updated Schema

- `accounts.Institution`
  - `status`
  - `is_deleted`
  - `created_by`
  - `updated_at`
- `accounts.User`
  - supports `super_admin`, `admin`, `teacher`, `student`, and management roles
  - scoped by `institution`
- `tenants.SubscriptionPlan`
  - `max_students`
  - `max_teachers`
  - `enabled_features`
  - `duration_days`
  - `price_monthly`
- `tenants.TenantSubscription`
  - current plan
  - status
  - expiry
  - per-tenant overrides
- `tenants.TenantDomain`
  - supports subdomain/domain routing
- `tenants.TenantUsageSnapshot`
  - tenant usage analytics
- `tenants.AuditLog`
  - who did what, when, and from where

## Tenant-Aware APIs

- `POST /api/login/`
  Returns JWT plus tenant metadata and feature flags.
- `GET /api/accounts/me/`
  Returns current role, tenant, and enabled features.
- `GET /api/tenants/dashboard/`
  Super-admin global SaaS metrics.
- `GET|POST /api/tenants/institutions/`
  List and provision tenants.
- `POST /api/tenants/institutions/{id}/suspend/`
- `POST /api/tenants/institutions/{id}/reactivate/`
- `POST /api/tenants/institutions/{id}/soft_delete/`
- `GET|POST /api/tenants/plans/`
- `GET|POST /api/tenants/subscriptions/`

Existing module routes remain tenant-aware through middleware + managers.

## Example Data Flow

1. User logs in through `/api/login/`.
2. JWT is issued with `tenant_id`, `user_id`, and `role`.
3. On each request, `TenantContextMiddleware` decodes the token.
4. Tenant-aware managers automatically scope querysets.
5. Role permissions are checked:
   - `super_admin`: global access
   - `admin`: own institution
   - `teacher/student`: limited views
6. Subscription service checks:
   - tenant status
   - expiry
   - plan feature flags
   - usage limits

## Subscription Enforcement Logic

- `tenants.services.enforce_subscription_state()`
  Blocks expired or suspended tenants.
- `tenants.services.ensure_feature_enabled()`
  Enables premium-only features such as analytics.
- `tenants.services.enforce_usage_limit()`
  Prevents new student/teacher creation if plan limits are exceeded.

## Frontend Structure

- `frontend/src/pages/SuperAdminDashboard.jsx`
  Global SaaS dashboard.
- `frontend/src/pages/TenantManagement.jsx`
  Tenant provisioning and lifecycle controls.
- Existing dashboards continue for:
  - institution admin
  - teacher
  - student
- `frontend/src/components/ProtectedRoute.jsx`
  now supports `super_admin`
- `frontend/src/components/Sidebar.jsx`
  now exposes tenant-management routes for `super_admin`

## Security Controls

- BCrypt password hashing enabled in Django settings.
- JWT claims restricted to required tenancy data.
- Tenant data scoped automatically in managers.
- Audit log generated for mutating HTTP operations.
- Feature access and subscription state enforced server-side.

## Verification

- `python manage.py check`
- `python manage.py test tenants.tests`
- `npm run build`
