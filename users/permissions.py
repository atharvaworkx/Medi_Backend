from rest_framework import permissions


class UsersPermission(permissions.BasePermission):
    # def has_permission(self, request, view):
    #         if request.user.is_authenticated:
    #             return True
    #         return False

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            if request.user.is_authenticated:
                return True
            return False

        if request.method == "POST":
            return True
        # Instance must have an attribute named email
        try:
            authorize = request.user.email == obj.email or request.user.is_superuser
            return authorize
        except Exception:
            return False


class IsOwnerOrAdminOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named email
        try:
            authorize = request.user.email == obj.userId.email or request.user.is_superuser
            return authorize
        except Exception:
            return False
