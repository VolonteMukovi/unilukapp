from django.db.models import Q
from drf_spectacular.utils import extend_schema

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from config.schema import crud_table
from messagerie.models import Message
from messagerie.serializers import MessageCreateSerializer, MessageSerializer


@crud_table(
    "Message",
    marquer_lu=extend_schema(
        tags=["Message"],
        summary="Marquer le message comme lu - Message",
    ),
)
class MessageViewSet(viewsets.ModelViewSet):
    http_method_names = ["get", "post", "head", "options"]
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ("expediteur", "destinataire", "lu", "parent")
    search_fields = ("sujet", "corps")
    ordering_fields = ("created_at", "lu")

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Message.objects.none()
        u = self.request.user
        qs = Message.objects.filter(Q(expediteur=u) | Q(destinataire=u))
        avec = self.request.query_params.get("avec")
        if avec:
            try:
                uid = int(avec)
            except (TypeError, ValueError):
                uid = None
            if uid is not None:
                qs = qs.filter(
                    Q(expediteur_id=uid, destinataire=u)
                    | Q(destinataire_id=uid, expediteur=u)
                )
        racine = self.request.query_params.get("racine_seulement")
        if racine and racine.lower() in ("1", "true", "oui"):
            qs = qs.filter(parent__isnull=True)
        return qs.select_related("expediteur", "destinataire", "parent").order_by("created_at")

    def get_serializer_class(self):
        if self.action == "create":
            return MessageCreateSerializer
        return MessageSerializer

    def perform_create(self, serializer):
        serializer.save(expediteur=self.request.user)

    @action(detail=True, methods=["post"], url_path="marquer-lu")
    def marquer_lu(self, request, pk=None):
        message = self.get_object()
        if message.destinataire_id != request.user.id:
            return Response(
                {"detail": "Seul le destinataire peut marquer le message comme lu."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if not message.lu:
            message.lu = True
            message.save(update_fields=["lu"])
        return Response(MessageSerializer(message).data)
