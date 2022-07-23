from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser, BasePermission
from rest_framework import exceptions as rest_exceptions

from django.core.exceptions import ValidationError


class IsOwnerOrReadOnly(BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        return obj.id == request.user.id or request.user.is_superuser


class PublicApiMixin:
    permission_classes = ()


class UserPermission:
    permission_classes_by_action = {
        "create": [AllowAny], "list": [IsAdminUser], "get": [IsAdminUser], "defalut": IsOwnerOrReadOnly}

    def get_permissions(self):
        try:
            # return permission_classes depending on `action`
            return [
                permission()
                for permission in self.permission_classes_by_action[self.action]
            ]
        except KeyError:
            # action is not set return default permission_classes
            return [self.permission_classes_by_action["defalut"]()]
