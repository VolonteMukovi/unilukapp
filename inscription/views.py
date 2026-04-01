from rest_framework import permissions, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from config.schema import crud_table
from inscription.filters import (
    AffectFiliereFilter,
    DomaineFilter,
    FiliereFilter,
    InstitutionFilter,
)
from inscription.models import AffectFiliere, Domaine, Filiere, Institution
from inscription.serializers import (
    AffectFiliereSerializer,
    DomaineSerializer,
    FiliereSerializer,
    InstitutionSerializer,
)
from users.permissions import IsRoleAdmin


@crud_table("Institution")
class InstitutionViewSet(viewsets.ModelViewSet):
    queryset = Institution.objects.all().order_by("nom")
    serializer_class = InstitutionSerializer
    filterset_class = InstitutionFilter
    search_fields = ("nom", "code", "adresse")
    ordering_fields = ("nom", "code", "created_at")

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsAuthenticated(), IsRoleAdmin()]


@crud_table("Domaine")
class DomaineViewSet(viewsets.ModelViewSet):
    queryset = Domaine.objects.select_related("institution").order_by("institution", "nom")
    serializer_class = DomaineSerializer
    filterset_class = DomaineFilter
    search_fields = ("nom", "code", "institution__nom")
    ordering_fields = ("nom", "code", "institution")

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsAuthenticated(), IsRoleAdmin()]


@crud_table("Filière")
class FiliereViewSet(viewsets.ModelViewSet):
    queryset = Filiere.objects.select_related("domaine__institution").order_by("domaine", "nom")
    serializer_class = FiliereSerializer
    filterset_class = FiliereFilter
    search_fields = ("nom", "code", "domaine__nom", "domaine__institution__nom")
    ordering_fields = ("nom", "code", "domaine")

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsAuthenticated(), IsRoleAdmin()]


@crud_table("AffectFiliere")
class AffectFiliereViewSet(viewsets.ModelViewSet):
    queryset = (
        AffectFiliere.objects.select_related("user", "filiere__domaine__institution")
        .all()
        .order_by("-id")
    )
    serializer_class = AffectFiliereSerializer
    filterset_class = AffectFiliereFilter
    ordering_fields = ("id", "date_debut", "date_fin")
    permission_classes = [permissions.IsAuthenticated, IsRoleAdmin]
