from drf_spectacular.utils import OpenApiExample, extend_schema, extend_schema_view
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from authentication.serializers import CustomTokenObtainPairSerializer


@extend_schema_view(
    post=extend_schema(
        tags=["Authentification"],
        summary=(
            "Connexion - jetons JWT + profil utilisateur. "
            "Fournir `password` et **au moins un** des champs `email` ou `num_tel` "
            "(équivalent JSON `numTel`). Inutile d’envoyer les deux."
        ),
        description=(
            "Le corps accepte `password` obligatoire, plus **soit** `email` **soit** `num_tel` "
            "(ou `numTel`). Réponse : `access`, `refresh`, `user` (profil avec filières imbriquées sur `/users/me/`)."
        ),
        examples=[
            OpenApiExample(
                "Connexion avec e-mail",
                value={"email": "user@example.com", "password": "motdepasse"},
                request_only=True,
            ),
            OpenApiExample(
                "Connexion avec numéro (snake_case)",
                value={"num_tel": "+243900000000", "password": "motdepasse"},
                request_only=True,
            ),
            OpenApiExample(
                "Connexion avec numTel (camelCase)",
                value={"numTel": "+243900000000", "password": "motdepasse"},
                request_only=True,
            ),
        ],
    ),
)
class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


@extend_schema_view(
    post=extend_schema(
        tags=["Authentification"],
        summary="Rafraîchir le jeton d'accès (refresh token)",
    ),
)
class RefreshView(TokenRefreshView):
    pass
