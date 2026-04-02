from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from inscription.models import Filiere
from users.models import User, UserRole
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

    @extend_schema_field(
        {
            "type": "string",
            "format": "uri",
            "nullable": True,
            "description": "URL absolue de la photo ; null si aucune image.",
        }
    )
    def get_photo_profil(self, obj):
        return absolute_photo_url(obj, self.context.get("request"))


class UserWriteSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6, required=False)

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
        v = value.lower().strip()
        qs = User.objects.filter(email__iexact=v)
        if self.instance is not None:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Cette adresse e-mail est déjà utilisée.")
        return v

    def validate_num_tel(self, value):
        try:
            normalized = validate_phone(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages)) from exc
        qs = User.objects.filter(num_tel=normalized)
        if self.instance is not None:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                "Ce numéro de téléphone est déjà utilisé par un autre compte."
            )
        return normalized

    def validate_matricule(self, value):
        if value is None:
            return None
        v = (value or "").strip()
        if not v:
            return None
        qs = User.objects.filter(matricule=v)
        if self.instance is not None:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Ce matricule est déjà utilisé.")
        return v

    def validate(self, attrs):
        request = self.context.get("request")
        if request and not request.user.is_authenticated:
            if not attrs.get("password"):
                raise serializers.ValidationError(
                    {"password": "Ce champ est obligatoire pour l'inscription."}
                )
            allowed_roles = {
                UserRole.ETUDIANT,
                UserRole.ADMIN,
                UserRole.SECRETAIRE,
            }
            role = attrs.get("role", UserRole.ETUDIANT)
            if role not in allowed_roles:
                role = UserRole.ETUDIANT
                attrs["role"] = role
            if role == UserRole.ETUDIANT and not attrs.get("matricule"):
                raise serializers.ValidationError(
                    {
                        "matricule": "Le matricule est obligatoire pour les comptes étudiants."
                    }
                )
            return attrs

        inst = self.instance
        role = attrs.get("role", inst.role if inst else UserRole.ETUDIANT)
        if inst is None:
            role = attrs.get("role", UserRole.ETUDIANT)

        if "matricule" in attrs:
            mat = attrs["matricule"]
        else:
            mat = inst.matricule if inst else None

        if role == UserRole.ETUDIANT and not mat:
            raise serializers.ValidationError(
                {"matricule": "Le matricule est obligatoire pour les comptes étudiants."}
            )
        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        if request and not request.user.is_authenticated:
            validated_data.pop("is_active", None)
            validated_data["is_active"] = True
        elif request and getattr(request.user, "role", None) != UserRole.ADMIN:
            validated_data.pop("role", None)
            validated_data.pop("is_active", None)
            validated_data["role"] = UserRole.ETUDIANT
            validated_data["is_active"] = True
        password = validated_data.pop("password", None)
        user = User(**validated_data)
        if password:
            try:
                validate_password(password, user)
            except DjangoValidationError as exc:
                raise serializers.ValidationError(
                    {"password": list(exc.messages)}
                ) from exc
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
            try:
                validate_password(password, instance)
            except DjangoValidationError as exc:
                raise serializers.ValidationError(
                    {"password": list(exc.messages)}
                ) from exc
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

    @extend_schema_field(
        {
            "type": "string",
            "format": "uri",
            "nullable": True,
            "description": "URL absolue de la photo ; null si aucune image.",
        }
    )
    def get_photo_profil(self, obj):
        return absolute_photo_url(obj, self.context.get("request"))

    def get_filieres(self, obj):
        qs = obj.filieres.select_related("domaine__institution").all()
        return FiliereNestedForUserSerializer(qs, many=True).data
