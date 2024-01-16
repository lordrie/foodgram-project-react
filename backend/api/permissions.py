from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Проверяет, является ли автором.
    Если нет, разрешает только безопасные методы."""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user
