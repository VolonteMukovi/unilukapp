from datetime import date, timedelta

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from inscription.models import Domaine, Filiere, Institution
from post.models import Horaire, HoraireStatut
from post.services.horaire_service import sync_horaires_expires
from users.models import User, UserRole


class HoraireExpireTests(TestCase):
    def setUp(self):
        inst = Institution.objects.create(nom="Uni", code="U1")
        dom = Domaine.objects.create(institution=inst, nom="Sciences")
        self.filiere = Filiere.objects.create(domaine=dom, nom="Info")
        self.user = User.objects.create_user(
            email="etu@test.local",
            password="SecurePass12",
            matricule="MAT-002",
            num_tel="+243900000002",
            first_name="Etu",
            last_name="Test",
            role=UserRole.ETUDIANT,
        )

    def test_sync_marks_past_horaires_expired(self):
        past_end = timezone.now().date() - timedelta(days=2)
        pdf = SimpleUploadedFile("cours.pdf", b"%PDF-1.4\n", content_type="application/pdf")
        h = Horaire.objects.create(
            filiere=self.filiere,
            fichier=pdf,
            date_debut=past_end - timedelta(days=7),
            date_fin=past_end,
            statut=HoraireStatut.ACTIF,
        )
        sync_horaires_expires()
        h.refresh_from_db()
        self.assertEqual(h.statut, HoraireStatut.EXPIRE)

    def test_student_sees_only_own_filiere_horaires(self):
        from inscription.models import AffectFiliere

        AffectFiliere.objects.create(user=self.user, filiere=self.filiere)
        Horaire.objects.create(
            filiere=self.filiere,
            fichier=SimpleUploadedFile("td.pdf", b"%PDF-1.4\n", content_type="application/pdf"),
            date_debut=date.today(),
            date_fin=date.today() + timedelta(days=30),
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        r = self.client.get("/api/horaires/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["count"], 1)
