from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from post.models import CategoriePost, Horaire, Publication, PublicationStatut
from post.validators import validate_horaire_fichier
from users.models import UserRole
from users.serializers import UserListSerializer


class CategoriePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriePost
        fields = ("id", "nom", "slug", "description", "students_can_manage")


class PublicationListSerializer(serializers.ModelSerializer):
    author = UserListSerializer(read_only=True)
    categorie_nom = serializers.CharField(source="categorie.nom", read_only=True)

    class Meta:
        model = Publication
        fields = (
            "id",
            "titre",
            "statut",
            "categorie",
            "categorie_nom",
            "author",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("author", "created_at", "updated_at")


class PublicationDetailSerializer(PublicationListSerializer):
    contenu = serializers.CharField()

    class Meta(PublicationListSerializer.Meta):
        fields = PublicationListSerializer.Meta.fields + ("contenu",)


class PublicationWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publication
        fields = ("id", "categorie", "titre", "contenu", "statut")
        read_only_fields = ("id",)

    def validate_statut(self, value):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if user and getattr(user, "role", None) == UserRole.ETUDIANT and value != PublicationStatut.ACTIF:
            raise serializers.ValidationError("Les étudiants ne peuvent pas archiver une publication.")
        return value


class HoraireSerializer(serializers.ModelSerializer):
    filiere_nom = serializers.CharField(source="filiere.nom", read_only=True)
    domaine_nom = serializers.CharField(source="filiere.domaine.nom", read_only=True)
    institution_nom = serializers.CharField(source="filiere.domaine.institution.nom", read_only=True)

    class Meta:
        model = Horaire
        fields = (
            "id",
            "filiere",
            "filiere_nom",
            "domaine_nom",
            "institution_nom",
            "description",
            "fichier",
            "date_debut",
            "date_fin",
            "statut",
        )
        read_only_fields = ("statut",)

    def validate_fichier(self, value):
        if value in (None, ""):
            return value
        try:
            validate_horaire_fichier(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages)) from exc
        return value

    def validate(self, attrs):
        debut = attrs.get("date_debut", getattr(self.instance, "date_debut", None))
        fin = attrs.get("date_fin", getattr(self.instance, "date_fin", None))
        if debut and fin and fin < debut:
            raise serializers.ValidationError(
                {"date_fin": "La date de fin doit être après la date de début."}
            )
        fichier = attrs.get("fichier")
        if self.instance is None and not fichier:
            raise serializers.ValidationError(
                {"fichier": "Un fichier PDF ou image contenant l’horaire est obligatoire."}
            )
        return attrs

    def to_representation(self, instance):
        data = super().to_representation(instance)
        f = instance.fichier
        if f:
            url = f.url
            request = self.context.get("request")
            data["fichier"] = request.build_absolute_uri(url) if request else url
        else:
            data["fichier"] = None
        return data
