from rest_framework import permissions
from accounts.models import UserType


class IsAdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):

        if request.method in permissions.SAFE_METHODS:
            return True

        return (
            request.user.user_type == UserType.ADMIN
            or request.user.user_type == UserType.SUPERUSER
        )
