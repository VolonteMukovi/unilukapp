import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

PHONE_RE = re.compile(r"^\+?[0-9][0-9\s\-]{7,18}[0-9]$")


def validate_phone(value: str):
    v = (value or "").strip()
    if not PHONE_RE.match(v):
        raise ValidationError(
            _("Format de numéro invalide. Utilisez 8 à 20 chiffres, espaces ou tirets, optionnellement + en tête.")
        )
    return v
