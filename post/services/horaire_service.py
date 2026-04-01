from post.models import Horaire


def sync_horaires_expires():
    """Met à jour en masse les horaires dont la date de fin est passée."""
    return Horaire.objects.sync_expired()
