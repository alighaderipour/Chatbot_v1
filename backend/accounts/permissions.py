from rest_framework import permissions


class IsStaffOrAdmin(permissions.BasePermission):
    """
    Tier 2+: staff members AND admins can pass this check (both have
    is_staff=True — that flag is what "grants dashboard access" at all).
    Used for read access and everyday management actions.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class IsAdmin(permissions.BasePermission):
    """
    Tier 3 only: true admins. We use Django's built-in is_superuser flag for
    this rather than a custom field — it already exists on every User row
    and already means "full permissions" by convention.

    Three tiers, two built-in flags:
      regular user  -> is_staff=False, is_superuser=False
      staff         -> is_staff=True,  is_superuser=False
      admin         -> is_staff=True,  is_superuser=True
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_superuser)
