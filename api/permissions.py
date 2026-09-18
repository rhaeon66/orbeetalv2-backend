from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import NotAuthenticated
from rest_framework.permissions import BasePermission


class BrowserSessionAuthentication(SessionAuthentication):
    """Same as SessionAuthentication, but unauthenticated requests return 401."""

    def authenticate_header(self, request):
        return "Session"


class IsStaffUser(BasePermission):
    message = "Admin access required."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            raise NotAuthenticated()
        return bool(user.is_staff)
