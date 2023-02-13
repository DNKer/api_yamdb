from rest_framework import permissions

from .role import ADMIN, MODERATOR


class IamOrReadOnly(permissions.BasePermission):
    """Собcтвенник, администратор или только чтение."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_superuser or request.user.role == ADMIN
            or obj == request.user)


class ChangeAdminOnly(permissions.BasePermission):
    """Изменение доступно только администратору."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and (request.user.is_superuser or request.user.role == ADMIN)
        )


class StaffOrReadOnly(permissions.BasePermission):
    """Администратор или только чтение."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or (request.user.is_authenticated and request.user.role == ADMIN)
        )


class AuthorOrStaffOrReadOnly(permissions.BasePermission):
    """Автор, модератор, админ или только чтение."""

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_superuser
            or request.user.role in (MODERATOR, ADMIN)
        )
