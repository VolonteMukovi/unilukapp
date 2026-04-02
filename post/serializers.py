from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from inscription.serializers import FiliereSerializer
from post.models import CategoriePost, Horaire, Publication, PublicationStatut
from post.validators import validate_horaire_fichier, validate_publication_image
from users.models import UserRole
from users.serializers import UserListSerializer


class CategoriePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriePost
        fields = ("id", "nom", "slug", "description", "students_can_manage")


class PublicationListSerializer(serializers.ModelSerializer):
    author_detail = UserListSerializer(source="author", read_only=True)
    categorie_detail = CategoriePostSerializer(source="categorie", read_only=True)

    class Meta:
        model = Publication
        fields = (
            "id",
            "titre",
            "type_pub",
            "statut",
            "categorie",
            "categorie_detail",
            "author",
            "author_detail",
            "image",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("author", "author_detail", "categorie_detail", "created_at", "updated_at")

    def to_representation(self, instance):
        data = super().to_representation(instance)
        img = instance.image
        if img:
            url = img.url
            request = self.context.get("request")
            data["image"] = request.build_absolute_uri(url) if request else url
        else:
            data["image"] = None
        return data


class PublicationDetailSerializer(PublicationListSerializer):
    contenu = serializers.CharField()

    class Meta(PublicationListSerializer.Meta):
        fields = PublicationListSerializer.Meta.fields + ("contenu",)


class PublicationWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publication
        fields = ("id", "categorie", "titre", "contenu", "type_pub", "statut", "image")
        read_only_fields = ("id",)
        extra_kwargs = {"image": {"required": False, "allow_null": True}}

    def validate_image(self, value):
        if value in (None, ""):
            return value
        try:
            validate_publication_image(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages)) from exc
        return value

    def validate_statut(self, value):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if user and getattr(user, "role", None) == UserRole.ETUDIANT and value != PublicationStatut.ACTIF:
            raise serializers.ValidationError("Les étudiants ne peuvent pas archiver une publication.")
        return value

    def to_representation(self, instance):
        return PublicationDetailSerializer(instance, context=self.context).data


class HoraireSerializer(serializers.ModelSerializer):
    filiere_detail = FiliereSerializer(source="filiere", read_only=True)

    class Meta:
        model = Horaire
        fields = (
            "id",
            "filiere",
            "filiere_detail",
            "description",
            "fichier",
            "date_debut",
            "date_fin",
            "statut",
        )
        read_only_fields = ("statut", "filiere_detail")

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
