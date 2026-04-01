from rest_framework import serializers

from inscription.models import AffectFiliere, Domaine, Filiere, Institution
from users.serializers import UserListSerializer


class InstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = ("id", "nom", "code", "adresse", "created_at", "updated_at")
        read_only_fields = ("created_at", "updated_at")


class DomaineSerializer(serializers.ModelSerializer):
    institution_nom = serializers.CharField(source="institution.nom", read_only=True)

    class Meta:
        model = Domaine
        fields = ("id", "institution", "institution_nom", "nom", "code")


class FiliereSerializer(serializers.ModelSerializer):
    domaine_nom = serializers.CharField(source="domaine.nom", read_only=True)
    institution_id = serializers.IntegerField(source="domaine.institution_id", read_only=True)
    institution_nom = serializers.CharField(source="domaine.institution.nom", read_only=True)

    class Meta:
        model = Filiere
        fields = (
            "id",
            "domaine",
            "domaine_nom",
            "institution_id",
            "institution_nom",
            "nom",
            "code",
        )


class AffectFiliereSerializer(serializers.ModelSerializer):
    user_detail = UserListSerializer(source="user", read_only=True)
    filiere_detail = FiliereSerializer(source="filiere", read_only=True)

    class Meta:
        model = AffectFiliere
        fields = (
            "id",
            "user",
            "filiere",
            "date_debut",
            "date_fin",
            "user_detail",
            "filiere_detail",
        )
        read_only_fields = ("user_detail", "filiere_detail")
