from drf_spectacular.utils import extend_schema

from rest_framework import mixins, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from config.schema import crud_table
from users.models import User, UserRole
from users.permissions import AllowAnonymousOrAdminCreate, IsRoleAdmin
from users.serializers import (
    UserListSerializer,
    UserMeUpdateSerializer,
    UserProfileSerializer,
    UserWriteSerializer,
)


@crud_table(
    "User",
    me=extend_schema(
        tags=["User"],
        summary="Profil connecté - lecture (GET) / mise à jour partielle (PATCH)",
        methods=["GET", "PATCH"],
    ),
)
class UserViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = User.objects.all().order_by("-date_joined")
    filterset_fields = ("role", "is_active")
    search_fields = (
        "email",
        "matricule",
        "first_name",
        "troisieme_nom",
        "last_name",
        "num_tel",
    )
    ordering_fields = ("date_joined", "email", "matricule", "role")

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return UserWriteSerializer
        return UserListSerializer

    def get_permissions(self):
        if self.action == "me":
            return [permissions.IsAuthenticated()]
        if self.action == "list":
            return [permissions.IsAuthenticated(), IsRoleAdmin()]
        if self.action == "create":
            return [AllowAnonymousOrAdminCreate()]
        if self.action == "destroy":
            return [permissions.IsAuthenticated(), IsRoleAdmin()]
        if self.action in ("retrieve", "update", "partial_update"):
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    def get_queryset(self):
        base = User.objects.all().order_by("-date_joined")
        user = self.request.user
        if not user.is_authenticated:
            return base.none()
        if getattr(user, "role", None) == UserRole.ADMIN:
            return base
        if self.action in ("retrieve", "update", "partial_update"):
            return base.filter(pk=user.pk)
        return base.none()

    @action(detail=False, methods=["get", "patch"], url_path="me")
    def me(self, request):
        if request.method == "GET":
            u = (
                User.objects.prefetch_related("filieres__domaine__institution")
                .get(pk=request.user.pk)
            )
            return Response(
                UserProfileSerializer(u, context={"request": request}).data
            )
        ser = UserMeUpdateSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        ser.is_valid(raise_exception=True)
        ser.save()
        u = (
            User.objects.prefetch_related("filieres__domaine__institution")
            .get(pk=request.user.pk)
        )
        return Response(
            UserProfileSerializer(u, context={"request": request}).data
        )
