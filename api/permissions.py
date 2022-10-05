from rest_framework import permissions


class IsOperator(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.is_operator:
            return True
        return False
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_operator:
            return True
        return False

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.is_admin:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_admin:
            return True
        return False
