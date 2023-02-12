from django.contrib.auth import get_user_model
from rest_framework import permissions


class IamOrReadOnly(permissions.BasePermission):
    """Сосбтвенник, администратор или только чтение."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_superuser or request.user.role == 'admin'
            or obj == request.user)


class ChangeAdminOnly(permissions.BasePermission):
    """Изменение доступно только администратору."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class StaffOrReadOnly(permissions.BasePermission):
    """Администратор или только чтение."""

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class IsStaff(permissions.BasePermission):
    """Автор, модератор, админ или только чтение."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or (
                request.user.is_authenticated and (
                    request.user == obj.author
                    or request.user.is_admin
                    or request.user.is_moderator
                )
            )
        )
