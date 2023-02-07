from rest_framework import permissions


class IamOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_superuser or request.user.role == 'admin'
            or obj == request.user)


class ChangeAdminOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and (request.user.is_superuser or request.user.role == 'admin')
        )

    def has_object_permission(self, request, view, obj):
        return (

            request.user.is_authenticated
            and (request.user.is_superuser or request.user.role == 'admin')
        )


class StaffOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or (request.user.is_authenticated and request.user.role == 'admin')
        )

    def has_object_permission(self, request, view, obj):
        return (

            request.method in permissions.SAFE_METHODS
            or (request.user.is_authenticated and request.user.role == 'admin')
        )


class AuthorOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            (request.method in permissions.SAFE_METHODS
             or request.user.is_authenticated)
        ) or (request.user.is_superuser or request.user.role == 'admin')

    def has_object_permission(self, request, view, obj):
        return (
            (request.method in permissions.SAFE_METHODS
             or obj.author == request.user)
        ) or (request.user.is_superuser or request.user.role == 'admin')


class ModeratorReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return (

            request.user.is_authenticated
            or request.user.is_superuser or request.user.role != 'user'
        )

    def has_object_permission(self, request, view, obj):
        return (

            obj.author == request.user
            or request.user.is_superuser or request.user.role != 'user')
