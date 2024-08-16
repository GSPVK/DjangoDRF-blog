from django.contrib.auth import get_user_model
from rest_framework import serializers

from blog.api.serializers.endpoints.comments import CommentListSerializer
from blog.models import Comment

User = get_user_model()


class CommentShortSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field='username', queryset=User.objects)

    class Meta:
        model = Comment
        fields = (
            'author',
            'text',
        )


class PaginatedCommentsSerializer(serializers.Serializer):
    results = CommentListSerializer(many=True)
    count = serializers.IntegerField()
    next = serializers.URLField(allow_null=True)
    previous = serializers.URLField(allow_null=True)
