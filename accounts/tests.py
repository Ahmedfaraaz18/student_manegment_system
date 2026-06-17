from django.test import TestCase


class AccountRoutingTests(TestCase):
    def test_public_register_institution_route_is_removed(self):
        response = self.client.post("/api/accounts/register-institution/", {})
        self.assertEqual(response.status_code, 404)
