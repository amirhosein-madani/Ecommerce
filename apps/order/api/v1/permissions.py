from rest_framework import permissions
from accounts.models import UserType


class IsCustomer(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.user_type == UserType.CUSTOMER
