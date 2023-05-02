from rest_framework import serializers
from pcf.models import Post


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'author', 'title', 'content', 'category', 'created_at', 'updated_at']