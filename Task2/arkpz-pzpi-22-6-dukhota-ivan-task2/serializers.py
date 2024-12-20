
# api/permissions.py

from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff

class IsStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'staff'

class IsParent(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'parent'

class IsStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'student'

class IsAdminOrStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and (request.user.is_staff or request.user.role == 'staff')
