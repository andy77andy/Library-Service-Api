from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view) -> bool:
        return True if request.method in SAFE_METHODS else request.user.is_staff
