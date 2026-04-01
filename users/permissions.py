from rest_framework import permissions

from users.models import UserRole


def _role(user):
    if not user or not user.is_authenticated:
        return None
    return getattr(user, "role", None)


class IsRoleAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return _role(request.user) == UserRole.ADMIN


class IsRoleSecretaireOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return _role(request.user) in (UserRole.ADMIN, UserRole.SECRETAIRE)


class IsAuthenticatedEtudiantOrAbove(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
