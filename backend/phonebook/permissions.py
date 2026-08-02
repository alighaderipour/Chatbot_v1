from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Any authenticated user can read (search/browse) the phonebook.
    Only a true admin (is_superuser) can create/edit/delete anything in it
    — matches "only admin can add stuff to phonebook."
    """

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user.is_superuser)
