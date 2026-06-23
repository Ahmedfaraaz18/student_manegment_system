from django.test import TestCase, override_settings


class AccountRoutingTests(TestCase):
    def test_public_register_institution_route_is_removed(self):
        response = self.client.post("/api/accounts/register-institution/", {})
        self.assertEqual(response.status_code, 404)

    @override_settings(CORS_ALLOW_ALL_ORIGINS=False)
    def test_deployed_frontend_origin_can_call_login(self):
        origin = "https://student_management_system-1.onrender.com"

        response = self.client.options(
            "/api/login/",
            HTTP_ORIGIN=origin,
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST",
            HTTP_ACCESS_CONTROL_REQUEST_HEADERS="content-type",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["access-control-allow-origin"], origin)
