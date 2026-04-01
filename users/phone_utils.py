"""
Normalisation des numéros avec la bibliothèque `phonenumbers` (libphonenumber).
"""

from __future__ import annotations

import phonenumbers
from django.conf import settings
from phonenumbers import NumberParseException, PhoneNumberFormat


def _default_region() -> str:
    return getattr(settings, "PHONE_DEFAULT_REGION", "CD") or "CD"


def parse_phone_to_e164(raw: str) -> str | None:
    """
    Retourne le numéro au format E.164 (ex. +243900123456) ou None si invalide.
    Si le numéro n'a pas de préfixe +, le pays par défaut (PHONE_DEFAULT_REGION) est utilisé.
    """
    raw = (raw or "").strip()
    if not raw:
        return None
    region = None if raw.startswith("+") else _default_region()
    try:
        parsed = phonenumbers.parse(raw, region)
    except NumberParseException:
        return None
    if not phonenumbers.is_valid_number(parsed):
        return None
    return phonenumbers.format_number(parsed, PhoneNumberFormat.E164)


def find_user_by_phone_for_login(raw: str):
    """
    Recherche un utilisateur par numéro : d'abord E.164, puis correspondance exacte
    sur la chaîne saisie (anciennes données non normalisées).
    """
    from users.models import User

    e164 = parse_phone_to_e164(raw)
    if e164:
        u = User.objects.filter(num_tel=e164).first()
        if u:
            return u
    stripped = (raw or "").strip()
    if stripped:
        return User.objects.filter(num_tel=stripped).first()
    return None
