from rest_framework import permissions

# this file is responsible for blocking access to API endpoints for non-staff users (views are managed in views.py)

class IsStaffUser(permissions.BasePermission):
    """
    Allows access only to staff users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated #and request.user.is_staff
    # comment out here so that only users with is_staff=True can access the API!