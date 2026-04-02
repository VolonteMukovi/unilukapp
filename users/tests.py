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

    def test_login_with_num_tel_only_no_email_key(self):
        r = self.client.post(
            "/api/auth/token/",
            {"num_tel": "+243 900 000 001", "password": "SecurePass12"},
            format="json",
        )
        self.assertEqual(r.status_code, 200)
        self.assertIn("access", r.data)
        self.assertEqual(r.data["user"]["email"], "admin@test.local")

    def test_login_with_numTel_camel_case_alias(self):
        r = self.client.post(
            "/api/auth/token/",
            {"numTel": "+243 900 000 001", "password": "SecurePass12"},
            format="json",
        )
        self.assertEqual(r.status_code, 200)
        self.assertIn("access", r.data)

    def test_registration_duplicate_phone_returns_400_not_500(self):
        r = self.client.post(
            "/api/users/",
            {
                "email": "autre@test.local",
                "password": "SecurePass12",
                "matricule": "MAT-DUP",
                "num_tel": "+243900000001",
                "first_name": "X",
                "last_name": "Y",
            },
            format="json",
        )
        self.assertEqual(r.status_code, 400)
        self.assertIn("num_tel", r.data)

    def test_login_requires_password_and_email_or_phone(self):
        r = self.client.post(
            "/api/auth/token/",
            {"password": "SecurePass12"},
            format="json",
        )
        self.assertEqual(r.status_code, 400)
        self.assertIn("non_field_errors", r.data)

        r2 = self.client.post(
            "/api/auth/token/",
            {"email": "admin@test.local"},
            format="json",
        )
        self.assertEqual(r2.status_code, 400)
        self.assertIn("password", r2.data)

    def test_public_registration_accepts_six_character_password(self):
        r = self.client.post(
            "/api/users/",
            {
                "email": "sixchar@test.local",
                "password": "Zx9mK2",
                "matricule": "MAT-099",
                "num_tel": "+243900000099",
                "first_name": "Six",
                "last_name": "Chars",
            },
            format="json",
        )
        self.assertEqual(r.status_code, 201)

    def test_public_registration_without_auth(self):
        r = self.client.post(
            "/api/users/",
            {
                "email": "nouveau@test.local",
                "password": "SecurePass12",
                "matricule": "MAT-100",
                "num_tel": "+243900000100",
                "first_name": "Jean",
                "last_name": "Dupont",
            },
            format="json",
        )
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data["email"], "nouveau@test.local")
        self.assertEqual(r.data["role"], UserRole.ETUDIANT)

    def test_public_registration_admin_without_matricule(self):
        r = self.client.post(
            "/api/users/",
            {
                "email": "newadmin@test.local",
                "password": "SecurePass12",
                "num_tel": "+243900000101",
                "first_name": "Admin",
                "last_name": "Nouveau",
                "role": UserRole.ADMIN,
            },
            format="json",
        )
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data["role"], UserRole.ADMIN)
        self.assertIsNone(r.data.get("matricule"))

    def test_public_registration_forces_active_even_if_client_sends_false(self):
        r = self.client.post(
            "/api/users/",
            {
                "email": "staff@test.local",
                "password": "SecurePass12",
                "num_tel": "+243900000102",
                "first_name": "S",
                "last_name": "T",
                "role": UserRole.SECRETAIRE,
                "is_active": False,
            },
            format="json",
        )
        self.assertEqual(r.status_code, 201)
        self.assertTrue(r.data["is_active"])

    def test_public_registration_etudiant_requires_matricule(self):
        r = self.client.post(
            "/api/users/",
            {
                "email": "sansmat@test.local",
                "password": "SecurePass12",
                "num_tel": "+243900000103",
                "first_name": "A",
                "last_name": "B",
            },
            format="json",
        )
        self.assertEqual(r.status_code, 400)
        self.assertIn("matricule", r.data)

    def test_logged_in_non_admin_cannot_create_user(self):
        etu = User.objects.create_user(
            email="etu@test.local",
            password="SecurePass12",
            matricule="MAT-200",
            num_tel="+243900000200",
            first_name="E",
            last_name="Tu",
            role=UserRole.ETUDIANT,
        )
        self.client.force_authenticate(user=etu)
        r = self.client.post(
            "/api/users/",
            {
                "email": "other@test.local",
                "password": "SecurePass12",
                "matricule": "MAT-201",
                "num_tel": "+243900000201",
                "first_name": "O",
                "last_name": "Ther",
            },
            format="json",
        )
        self.assertEqual(r.status_code, 403)

    def test_admin_can_create_secretaire_without_matricule(self):
        self.client.force_authenticate(user=self.user)
        r = self.client.post(
            "/api/users/",
            {
                "email": "sec@test.local",
                "password": "SecurePass12",
                "num_tel": "+243900000150",
                "first_name": "Sec",
                "last_name": "Retaire",
                "role": UserRole.SECRETAIRE,
            },
            format="json",
        )
        self.assertEqual(r.status_code, 201)
        self.assertIsNone(r.data.get("matricule"))

    def test_admin_cannot_create_etudiant_without_matricule(self):
        self.client.force_authenticate(user=self.user)
        r = self.client.post(
            "/api/users/",
            {
                "email": "et2@test.local",
                "password": "SecurePass12",
                "num_tel": "+243900000151",
                "first_name": "E",
                "last_name": "T",
                "role": UserRole.ETUDIANT,
            },
            format="json",
        )
        self.assertEqual(r.status_code, 400)
