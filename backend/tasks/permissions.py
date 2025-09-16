from rest_framework.permissions import BasePermission
from accounts.models import User

class IsTaskOwner(BasePermission):
    """
    Permission to check if request.user is the assigned_to for the task.
    """
    def has_object_permission(self, request, view, obj):
        return obj.assigned_to == request.user

class IsAdminOrSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.role in (User.Role.ADMIN, User.Role.SUPERADMIN))
