from django.test import TestCase
from rest_framework.test import APIClient

from users.models import User, UserRole


class LoginApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="admin@test.local",
            password="SecurePass12",
            matricule="MAT-001",
            num_tel="+243900000001",
            first_name="Admin",
            last_name="Test",
            role=UserRole.ADMIN,
        )

    def test_login_returns_tokens_and_user_profile(self):
        r = self.client.post(
            "/api/auth/token/",
            {"email": "admin@test.local", "password": "SecurePass12"},
            format="json",
        )
        self.assertEqual(r.status_code, 200)
        self.assertIn("access", r.data)
        self.assertIn("refresh", r.data)
        self.assertIn("user", r.data)
        self.assertEqual(r.data["user"]["email"], "admin@test.local")
        self.assertEqual(r.data["user"]["role"], UserRole.ADMIN)

    def test_login_with_phone_number_in_email_field(self):
        r = self.client.post(
            "/api/auth/token/",
            {"email": "+243 900 000 001", "password": "SecurePass12"},
            format="json",
        )
        self.assertEqual(r.status_code, 200)
        self.assertIn("access", r.data)
        self.assertEqual(r.data["user"]["email"], "admin@test.local")
