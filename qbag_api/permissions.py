from rest_framework import permissions

class IsOther(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.user_type=="other"

class IsTeacher(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.user_type=="teacher"