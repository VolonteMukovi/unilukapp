from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from authentication.serializers import CustomTokenObtainPairSerializer


@extend_schema_view(
    post=extend_schema(
        tags=["Authentification"],
        summary="Connexion - jetons JWT + objet utilisateur (profil, filières, institution)",
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
