from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from inscription.models import Filiere
from users.models import User
from users.validators import validate_phone


def absolute_photo_url(user: User, request) -> str | None:
    if not user.photo_profil:
        return None
    url = user.photo_profil.url
    if request:
        return request.build_absolute_uri(url)
    return url


class UserListSerializer(serializers.ModelSerializer):
    photo_profil = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "matricule",
            "num_tel",
            "first_name",
            "troisieme_nom",
            "last_name",
            "photo_profil",
            "role",
            "is_active",
            "date_joined",
        )
        read_only_fields = fields

    def get_photo_profil(self, obj):
        return absolute_photo_url(obj, self.context.get("request"))


class UserWriteSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, required=False)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "matricule",
            "num_tel",
            "first_name",
            "troisieme_nom",
            "last_name",
            "photo_profil",
            "role",
            "is_active",
            "password",
        )
        read_only_fields = ("id",)

    def validate_email(self, value):
        return value.lower().strip()

    def validate_num_tel(self, value):
        try:
            return validate_phone(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages)) from exc

    def validate_matricule(self, value):
        v = (value or "").strip()
        if not v:
            raise serializers.ValidationError("Le matricule est obligatoire.")
        return v

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = User(**validated_data)
        if password:
            validate_password(password, user)
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        if password:
            validate_password(password, instance)
            instance.set_password(password)
        instance.save()
        return instance


class UserMeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("first_name", "troisieme_nom", "last_name", "num_tel", "photo_profil")
        extra_kwargs = {"num_tel": {"required": False}, "photo_profil": {"required": False}}

    def validate_num_tel(self, value):
        if value in (None, ""):
            return value
        try:
            return validate_phone(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages)) from exc


class FiliereNestedForUserSerializer(serializers.ModelSerializer):
    domaine_nom = serializers.CharField(source="domaine.nom", read_only=True)
    institution_nom = serializers.CharField(source="domaine.institution.nom", read_only=True)
    institution_id = serializers.IntegerField(source="domaine.institution_id", read_only=True)
    domaine_id = serializers.IntegerField(source="domaine_id", read_only=True)

    class Meta:
        model = Filiere
        fields = ("id", "nom", "code", "domaine_id", "domaine_nom", "institution_id", "institution_nom")


class UserProfileSerializer(serializers.ModelSerializer):
    filieres = serializers.SerializerMethodField()
    photo_profil = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "matricule",
            "num_tel",
            "first_name",
            "troisieme_nom",
            "last_name",
            "photo_profil",
            "role",
            "is_active",
            "date_joined",
            "filieres",
        )
        read_only_fields = fields

    def get_photo_profil(self, obj):
        return absolute_photo_url(obj, self.context.get("request"))

    def get_filieres(self, obj):
        qs = obj.filieres.select_related("domaine__institution").all()
        return FiliereNestedForUserSerializer(qs, many=True).data
