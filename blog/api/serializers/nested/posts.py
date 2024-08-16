from django.contrib.auth import get_user_model
from rest_framework import serializers

from blog.api.serializers.endpoints.posts import PostSerializer

User = get_user_model()


class PaginatedPostsSerializer(serializers.Serializer):
    results = PostSerializer(many=True)
    count = serializers.IntegerField()
    next = serializers.URLField(allow_null=True)
    previous = serializers.URLField(allow_null=True)
