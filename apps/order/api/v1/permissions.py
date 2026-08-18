from rest_framework import permissions
from accounts.models import UserType


class IsCustomer(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.user_type == UserType.CUSTOMER


class IsAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.user.user_type == UserType.ADMIN
            or request.user.user_type == UserType.SUPERUSER
        )
