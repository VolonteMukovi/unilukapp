from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from users.phone_utils import parse_phone_to_e164


def validate_phone(value: str) -> str:
    """
    Valide le numéro via `phonenumbers` et retourne la forme E.164 pour stockage cohérent.
    Une chaîne vide lève une erreur (champ obligatoire à la création).
    """
    if value in (None, ""):
        raise ValidationError(_("Le numéro de téléphone est obligatoire."))
    e164 = parse_phone_to_e164(value)
    if e164 is None:
        raise ValidationError(
            _(
                "Numéro de téléphone invalide. Utilisez un format international "
                "(ex. +243…) ou un numéro national valide pour la région configurée."
            )
        )
    return e164
