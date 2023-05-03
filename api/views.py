from django.db.models import Count
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import Group

from pcf.models import *
from .serializers import PostListGetSerializer, PostListPostSerializer, PostSingleSerializer, CommentSerializer, \
    CommentAddSerializer, CommentPostSerializer
from .permissions import IsVerified


class PostListAPIView(generics.ListCreateAPIView):
    queryset = Post.objects.order_by('-created_at').select_related('author').annotate(comments_count=Count('comments'))

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PostListGetSerializer
        elif self.request.method == 'POST':
            return PostListPostSerializer

    def perform_create(self, serializer):
        author = self.request.user
        if author.is_authenticated and author.groups.get(name='verified_users').exists():
            return serializer.save(author=author)
        else:
            raise PermissionDenied('Только авторизованные пользователи, подтвердившие email, могут создавать посты.')


class PersonalPageView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsVerified]
    serializer_class = CommentPostSerializer

    def get_queryset(self):
        return Comment.objects.filter(post__author=self.request.user)


class PostSingleView(RetrieveUpdateAPIView):
    queryset = Post.objects.all().prefetch_related('comments').select_related('author')

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return PostListPostSerializer
        else:
            return PostSingleSerializer

    def perform_update(self, serializer):
        if self.request.user != serializer.instance.author:
            raise PermissionDenied('Только автор может изменять объявление')
        serializer.save()


class CommentAddAPIView(generics.CreateAPIView):
    serializer_class = CommentAddSerializer
    permission_classes = [IsAuthenticated, IsVerified]

    def perform_create(self, serializer):
        post = Post.objects.get(id=self.kwargs.get('post_id'))
        serializer.save(author=self.request.user, post=post)


@api_view()
@permission_classes([IsAuthenticated, IsVerified])
def subscribe(request):
    if request.user.groups.filter(name='subscribed_users').exists():
        return Response({'detail': 'Вы уже подписаны на новостную рассылку.'})
    subscribed_user = Group.objects.get(name='subscribed_users')
    subscribed_user.user_set.add(request.user)
    return Response({'detail': 'Вы подписаны на новостную рассылку.'})


@api_view()
@permission_classes([IsAuthenticated, IsVerified])
def unsubscribe(request):
    if not request.user.groups.filter(name='subscribed_users').exists():
        return Response({'detail': 'Вы не были подписаны на новостную рассылку.'})
    subscribed_user = Group.objects.get(name='subscribed_users')
    subscribed_user.user_set.remove(request.user)
    return Response({'detail': 'Вы отписались от новостной рассылки.'})
