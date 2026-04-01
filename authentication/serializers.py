from django.contrib.auth import authenticate
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, update_last_login
from rest_framework_simplejwt.settings import api_settings as jwt_api_settings

from users.models import User
from users.phone_utils import find_user_by_phone_for_login
from users.serializers import UserProfileSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Connexion avec le champ `email` (USERNAME_FIELD) : accepte une adresse e-mail
    **ou** un numéro de téléphone (toute forme reconnue par libphonenumber).
    """

    default_error_messages = {
        **TokenObtainPairSerializer.default_error_messages,
        "invalid_credentials": "Identifiants incorrects.",
    }

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        token["email"] = user.email
        return token

    def validate(self, attrs):
        request = self.context.get("request")
        identifier = (attrs.get(self.username_field) or "").strip()
        password = attrs.get("password")

        if not identifier or not password:
            raise AuthenticationFailed(
                self.error_messages["invalid_credentials"],
                code="invalid_credentials",
            )

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
