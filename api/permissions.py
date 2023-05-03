from rest_framework import permissions
from django.contrib.auth.models import Group


class IsVerified(permissions.BasePermission):
    """Check whether user verified email"""
    message = 'Вы должны подтвержить свой email для совершения данного действия.'

    def has_permission(self, request, view):
        return request.user.groups.filter(name='verified_users').exists()
