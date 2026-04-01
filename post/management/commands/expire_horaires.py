from django.core.management.base import BaseCommand

from post.services.horaire_service import sync_horaires_expires


class Command(BaseCommand):
    help = "Archive (statut expiré) les horaires dont la date de fin est passée."

    def handle(self, *args, **options):
        n = sync_horaires_expires()
        self.stdout.write(self.style.SUCCESS(f"{n} horaire(s) mis à jour vers « expiré »."))
