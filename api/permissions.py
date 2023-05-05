from rest_framework import permissions
from django.contrib.auth.models import Group

from pcf.views import Post


class IsVerified(permissions.BasePermission):
    """Check whether user verified email"""
    message = 'Вы должны подтвержить свой email для совершения данного действия.'

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name='verified_users').exists()


class IsAuthor(permissions.BasePermission):
    message = 'Только автор поста может совершать данное действие'

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user

