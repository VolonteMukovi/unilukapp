import os

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

HORAIRE_FICHIER_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".webp", ".gif"}
HORAIRE_FICHIER_MAX_SIZE = 15 * 1024 * 1024  # 15 Mo

PUBLICATION_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
PUBLICATION_IMAGE_MAX_SIZE = 10 * 1024 * 1024  # 10 Mo


def validate_horaire_fichier(file):
    if file is None:
        return file
    name = getattr(file, "name", "") or ""
    ext = os.path.splitext(name.lower())[1]
    if ext not in HORAIRE_FICHIER_EXTENSIONS:
        raise ValidationError(
            _("Extension non autorisée. Formats acceptés : PDF, JPEG, PNG, WebP, GIF.")
        )
    size = getattr(file, "size", None)
    if size is not None and size > HORAIRE_FICHIER_MAX_SIZE:
        raise ValidationError(_("Le fichier ne doit pas dépasser 15 Mo."))
    return file


def validate_publication_image(file):
    """Image d’illustration pour une publication (optionnelle)."""
    if file is None:
        return file
    name = getattr(file, "name", "") or ""
    ext = os.path.splitext(name.lower())[1]
    if ext not in PUBLICATION_IMAGE_EXTENSIONS:
        raise ValidationError(
            _("Extension non autorisée. Images acceptées : JPEG, PNG, WebP, GIF.")
        )
    size = getattr(file, "size", None)
    if size is not None and size > PUBLICATION_IMAGE_MAX_SIZE:
        raise ValidationError(_("L’image ne doit pas dépasser 10 Mo."))
    return file
