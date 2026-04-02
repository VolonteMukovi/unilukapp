from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, update_last_login
from rest_framework_simplejwt.settings import api_settings as jwt_api_settings

from users.models import User
from users.phone_utils import find_user_by_phone_for_login
from users.serializers import UserProfileSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Connexion : fournir `password` et au moins un des champs `email` ou `num_tel`
    (alias JSON `numTel`). L’e-mail et le téléphone sont tous deux optionnels
    tant que l’un des deux est renseigné.
    """

    default_error_messages = {
        **TokenObtainPairSerializer.default_error_messages,
        "invalid_credentials": "Identifiants incorrects.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uname = self.fields[self.username_field]
        uname.required = False
        uname.allow_blank = True
        self.fields["num_tel"] = serializers.CharField(
            required=False,
            allow_blank=True,
            write_only=True,
        )

    def to_internal_value(self, data):
        if isinstance(data, dict):
            data = {**data}
            if "numTel" in data and "num_tel" not in data:
                data["num_tel"] = data["numTel"]
        return super().to_internal_value(data)

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        token["email"] = user.email
        return token

    def validate(self, attrs):
        request = self.context.get("request")
        email = (attrs.get(self.username_field) or "").strip()
        num_tel = (attrs.get("num_tel") or "").strip()
        password = attrs.get("password")

        errors = {}
        if not password:
            errors["password"] = ["Ce champ est obligatoire."]
        if not email and not num_tel:
            errors["non_field_errors"] = [
                "Fournissez une adresse e-mail ou un numéro de téléphone."
            ]
        if errors:
            raise serializers.ValidationError(errors)

        identifier = email if email else num_tel

        user = None
        if "@" in identifier:
            user = authenticate(
                request,
                **{self.username_field: identifier.lower(), "password": password},
            )
        else:
            candidate = find_user_by_phone_for_login(identifier)
            if (
                candidate
                and candidate.is_active
                and candidate.check_password(password)
            ):
                user = candidate

        if user is None:
            raise AuthenticationFailed(
                self.error_messages["no_active_account"],
                code="no_active_account",
            )

        if not jwt_api_settings.USER_AUTHENTICATION_RULE(user):
            raise AuthenticationFailed(
                self.error_messages["no_active_account"],
                code="no_active_account",
            )

        self.user = user

        refresh = self.get_token(user)
        data = {"refresh": str(refresh), "access": str(refresh.access_token)}

        if jwt_api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, user)

        user = User.objects.prefetch_related("filieres__domaine__institution").get(
            pk=user.pk
        )
        data["user"] = UserProfileSerializer(user, context=self.context).data
        return data
