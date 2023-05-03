from rest_framework import serializers
from pcf.models import Post, Comment
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username']


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer()
    class Meta:
        model = Comment
        fields = ['author', 'text', 'created_at', 'accepted']


class PostListGetSerializer(serializers.ModelSerializer):
    author = UserSerializer()
    comments_count = serializers.IntegerField()
    category_name = serializers.CharField(source='get_category_display')

    class Meta:
        model = Post
        fields = ['id', 'author', 'title', 'category_name', 'created_at', 'comments_count']


class PostListPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['title', 'category', 'content']


class PostSingleSerializer(serializers.ModelSerializer):
    author = UserSerializer()
    category_name = serializers.CharField(source='get_category_display')
    comments = CommentSerializer(many=True)
    class Meta:
        model = Post
        fields = ['author', 'title', 'category_name', 'content',  'comments', 'created_at', 'updated_at']


class CommentAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['text']


class CommentPostSerializer(serializers.ModelSerializer):
    post_title = serializers.CharField(source='post')
    author_name = serializers.CharField(source='author')
    class Meta:
        model = Comment
        fields = ['post_title', 'author_name', 'text', 'created_at']
