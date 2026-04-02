from drf_spectacular.utils import OpenApiExample

from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import SAFE_METHODS, AllowAny, BasePermission, IsAuthenticated

from config.openapi_examples import HORAIRE as HORAIRE_EXAMPLE
from config.openapi_examples import PAGINATED_HORAIRES as PAGINATED_HORAIRES_EXAMPLE
from config.openapi_examples import PAGINATED_PUBLICATIONS as PAGINATED_PUBLICATIONS_EXAMPLE
from config.openapi_examples import PUBLICATION as PUBLICATION_EXAMPLE
from config.schema import crud_table
from post.filters import CategoriePostFilter, HoraireFilter, PublicationFilter
from post.models import CategoriePost, Horaire, HoraireStatut, Publication, PublicationStatut
from post.serializers import (
    CategoriePostSerializer,
    HoraireSerializer,
    PublicationDetailSerializer,
    PublicationListSerializer,
    PublicationWriteSerializer,
)
from post.services.horaire_service import sync_horaires_expires
from users.models import UserRole
from users.permissions import IsRoleAdmin, IsRoleSecretaireOrAdmin


class PublicationAccessPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            if not request.user.is_authenticated:
                return obj.statut == PublicationStatut.ACTIF
            if getattr(request.user, "role", None) == UserRole.ETUDIANT:
                return obj.statut == PublicationStatut.ACTIF
            return True
        user = request.user
        role = getattr(user, "role", None)
        if role == UserRole.ADMIN:
            return True
        if role == UserRole.SECRETAIRE:
            return True
        if role == UserRole.ETUDIANT:
            return (
                obj.author_id == user.id
                and obj.categorie.students_can_manage
            )
        return False


@crud_table("CategoriePost")
class CategoriePostViewSet(viewsets.ModelViewSet):
    queryset = CategoriePost.objects.all().order_by("nom")
    serializer_class = CategoriePostSerializer
    filterset_class = CategoriePostFilter
    search_fields = ("nom", "slug", "description")
    ordering_fields = ("nom", "slug")

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsAuthenticated(), IsRoleAdmin()]


@crud_table(
    "Publication",
    list_examples=[
        OpenApiExample(
            "Liste paginée (author_detail, categorie_detail)",
            value=PAGINATED_PUBLICATIONS_EXAMPLE,
            response_only=True,
        ),
    ],
    retrieve_examples=[
        OpenApiExample(
            "Détail publication (contenu + nested)",
            value=PUBLICATION_EXAMPLE,
            response_only=True,
        ),
    ],
)
class PublicationViewSet(viewsets.ModelViewSet):
    filterset_class = PublicationFilter
    search_fields = ("titre", "contenu", "author__email", "author__matricule", "categorie__nom")
    ordering_fields = ("created_at", "updated_at", "titre", "statut", "type_pub")
    permission_classes = [PublicationAccessPermission]

    def get_queryset(self):
        qs = Publication.objects.select_related("author", "categorie").all()
        user = self.request.user
        if not user.is_authenticated:
            return qs.filter(statut=PublicationStatut.ACTIF)
        if getattr(user, "role", None) == UserRole.ETUDIANT:
            return qs.filter(statut=PublicationStatut.ACTIF)
        return qs

    def get_serializer_class(self):
        if self.action == "list":
            return PublicationListSerializer
        if self.action in ("create", "update", "partial_update"):
            return PublicationWriteSerializer
        return PublicationDetailSerializer

    def perform_create(self, serializer):
        user = self.request.user
        role = getattr(user, "role", None)
        categorie = serializer.validated_data.get("categorie")
        if role == UserRole.ETUDIANT:
            if not categorie.students_can_manage:
                raise PermissionDenied(
                    "Vous ne pouvez pas publier dans cette catégorie."
                )
        elif role not in (UserRole.ADMIN, UserRole.SECRETAIRE):
            raise PermissionDenied()
        serializer.save(author=user)

    def perform_update(self, serializer):
        self._guard_write(serializer.instance)
        serializer.save()

    def perform_destroy(self, instance):
        self._guard_write(instance)
        instance.delete()

    def _guard_write(self, publication):
        user = self.request.user
        role = getattr(user, "role", None)
        if role == UserRole.ADMIN:
            return
        if role == UserRole.SECRETAIRE:
            return
        if role == UserRole.ETUDIANT:
            if (
                publication.author_id == user.id
                and publication.categorie.students_can_manage
            ):
                return
        raise PermissionDenied()


@crud_table(
    "Horaire",
    list_examples=[
        OpenApiExample(
            "Liste paginée (filiere_detail imbriqué)",
            value=PAGINATED_HORAIRES_EXAMPLE,
            response_only=True,
        ),
    ],
    retrieve_examples=[
        OpenApiExample(
            "Détail horaire",
            value=HORAIRE_EXAMPLE,
            response_only=True,
        ),
    ],
)
class HoraireViewSet(viewsets.ModelViewSet):
    serializer_class = HoraireSerializer
    filterset_class = HoraireFilter
    search_fields = ("description", "filiere__nom")
    ordering_fields = ("date_debut", "date_fin", "statut", "filiere")

    def get_queryset(self):
        sync_horaires_expires()
        qs = Horaire.objects.select_related("filiere__domaine__institution").all()
        user = self.request.user
        if not user.is_authenticated:
            return qs.filter(statut=HoraireStatut.ACTIF)
        role = getattr(user, "role", None)
        if role == UserRole.ETUDIANT:
            if not user.affectations_filiere.exists():
                return qs.none()
            filiere_ids = user.affectations_filiere.values_list("filiere_id", flat=True)
            return qs.filter(filiere_id__in=filiere_ids, statut=HoraireStatut.ACTIF)
        if role in (UserRole.ADMIN, UserRole.SECRETAIRE):
            return qs
        return qs.filter(statut=HoraireStatut.ACTIF)

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        return [IsAuthenticated(), IsRoleSecretaireOrAdmin()]

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()
