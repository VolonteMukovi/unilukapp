from rest_framework import serializers

from inscription.models import AffectFiliere, Domaine, Filiere, Institution
from users.serializers import UserListSerializer


class InstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = ("id", "nom", "code", "adresse", "created_at", "updated_at")
        read_only_fields = ("created_at", "updated_at")


class DomaineSerializer(serializers.ModelSerializer):
    institution_detail = InstitutionSerializer(source="institution", read_only=True)

    class Meta:
        model = Domaine
        fields = ("id", "institution", "institution_detail", "nom", "code")


class FiliereSerializer(serializers.ModelSerializer):
    domaine_detail = DomaineSerializer(source="domaine", read_only=True)

    class Meta:
        model = Filiere
        fields = ("id", "domaine", "domaine_detail", "nom", "code")


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
        read_only_fields = (
            "user_detail",
            "filiere_detail",
        )
