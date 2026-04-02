from rest_framework import serializers

from messagerie.models import Message
from users.models import User
from users.serializers import UserListSerializer


class MessageParentBriefSerializer(serializers.ModelSerializer):
    """Message parent : FK + détails expéditeur/destinataire (pas de parent_detail récursif)."""

    expediteur_detail = UserListSerializer(source="expediteur", read_only=True)
    destinataire_detail = UserListSerializer(source="destinataire", read_only=True)

    class Meta:
        model = Message
        fields = (
            "id",
            "expediteur",
            "expediteur_detail",
            "destinataire",
            "destinataire_detail",
            "parent",
            "sujet",
            "corps",
            "lu",
            "created_at",
        )


class MessageSerializer(serializers.ModelSerializer):
    expediteur_detail = UserListSerializer(source="expediteur", read_only=True)
    destinataire_detail = UserListSerializer(source="destinataire", read_only=True)
    parent_detail = MessageParentBriefSerializer(
        source="parent", read_only=True, allow_null=True
    )

    class Meta:
        model = Message
        fields = (
            "id",
            "expediteur",
            "expediteur_detail",
            "destinataire",
            "destinataire_detail",
            "parent",
            "parent_detail",
            "sujet",
            "corps",
            "lu",
            "created_at",
        )
        read_only_fields = (
            "expediteur",
            "expediteur_detail",
            "destinataire_detail",
            "parent_detail",
            "lu",
            "created_at",
        )


class MessageCreateSerializer(serializers.ModelSerializer):
    destinataire = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Message
        fields = ("destinataire", "parent", "sujet", "corps")

    def validate(self, attrs):
        request = self.context["request"]
        user = request.user
        parent = attrs.get("parent")
        destinataire = attrs.get("destinataire")
        if parent:
            if user.id not in (parent.expediteur_id, parent.destinataire_id):
                raise serializers.ValidationError(
                    {"parent": "Vous ne participez pas à cette conversation."}
                )
            attrs["destinataire"] = (
                parent.destinataire if parent.expediteur_id == user.id else parent.expediteur
            )
        elif not destinataire:
            raise serializers.ValidationError(
                {"destinataire": "Obligatoire pour un nouveau fil (sans parent)."}
            )
        if not parent and destinataire and destinataire.pk == user.pk:
            raise serializers.ValidationError(
                {"destinataire": "Vous ne pouvez pas vous adresser un message à vous-même."}
            )
        return attrs
