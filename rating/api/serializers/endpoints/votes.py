from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers

from rating.models import PostRating, CommentRating


@extend_schema_serializer(exclude_fields=['obj', 'owner', 'vote'])
class PostVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostRating
        fields = (
            'obj',
            'owner',
            'vote'
        )


@extend_schema_serializer(exclude_fields=['obj', 'owner', 'vote'])
class CommentVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentRating
        fields = (
            'obj',
            'owner',
            'vote'
        )
