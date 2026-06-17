from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import InstitutionSettings
from .permissions import IsManagementRole
from .serializers import InstitutionSettingsSerializer
from .tenancy import get_user_institution
from tenants.services import enforce_subscription_state, get_feature_flags


def _auth_payload(user):
    institution = get_user_institution(user)
    settings = getattr(institution, "settings", None) if institution else None
    return {
        "role": user.role,
        "username": user.username,
        "tenant_id": institution.id if institution else None,
        "features": get_feature_flags(institution),
        "institution": {
            "id": institution.id,
            "name": institution.name,
            "code": institution.code,
            "institution_type": institution.institution_type,
            "short_name": settings.short_name if settings else institution.name,
        }
        if institution
        else None,
    }


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        username = (request.data.get("username") or "").strip()
        password = request.data.get("password") or ""
        user = authenticate(username=username, password=password)

        if user is None:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        if not user.is_active:
            return Response({"detail": "Account is inactive"}, status=status.HTTP_403_FORBIDDEN)
        if user.role != user.SUPER_ADMIN:
            try:
                enforce_subscription_state(get_user_institution(user))
            except Exception as exc:
                return Response({"detail": str(exc)}, status=status.HTTP_403_FORBIDDEN)

        refresh = RefreshToken.for_user(user)
        refresh["user_id"] = user.id
        refresh["role"] = user.role
        refresh["tenant_id"] = getattr(get_user_institution(user), "id", None)
        return Response(
            {
                "token": str(refresh.access_token),
                "refresh": str(refresh),
                **_auth_payload(user),
            }
        )

class InstitutionSettingsView(APIView):
    permission_classes = [IsAuthenticated, IsManagementRole]

    def get(self, request, *args, **kwargs):
        institution = get_user_institution(request.user)
        settings_obj, _ = InstitutionSettings.objects.get_or_create(
            institution=institution,
            defaults={"short_name": institution.name, "support_email": institution.contact_email},
        )
        return Response(InstitutionSettingsSerializer(settings_obj).data)

    def put(self, request, *args, **kwargs):
        institution = get_user_institution(request.user)
        settings_obj, _ = InstitutionSettings.objects.get_or_create(
            institution=institution,
            defaults={"short_name": institution.name, "support_email": institution.contact_email},
        )
        serializer = InstitutionSettingsSerializer(settings_obj, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    institution = get_user_institution(request.user)
    return Response(
        {
            "username": request.user.username,
            "email": request.user.email,
            "role": request.user.role,
            "tenant_id": institution.id if institution else None,
            "features": get_feature_flags(institution),
            "institution": {
                "id": institution.id,
                "name": institution.name,
                "code": institution.code,
                "institution_type": institution.institution_type,
                "short_name": getattr(getattr(institution, "settings", None), "short_name", institution.name),
            }
            if institution
            else None,
        }
    )
