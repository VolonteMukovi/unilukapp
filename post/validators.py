import os

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

HORAIRE_FICHIER_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".webp", ".gif"}
HORAIRE_FICHIER_MAX_SIZE = 15 * 1024 * 1024  # 15 Mo


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
