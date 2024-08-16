from typing import Optional, List

from django.core.exceptions import ObjectDoesNotExist
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from blog.api.serializers import mixins
from blog.api.serializers.endpoints.comments import CommentListSerializer
from blog.models import Author, Post
from common.mixins import serializers as common_s


class PostSerializer(common_s.TruncateTextSerializer, mixins.PostSerializerExtendedMixin):
    ...


class PostRetrieveWithCommentsSerializer(mixins.PostSerializerExtendedMixin):
    comments = serializers.SerializerMethodField()

    @extend_schema_field(CommentListSerializer)
    def get_comments(self, obj) -> Optional[List[CommentListSerializer]]:
        return self.context.get('comments')

    class Meta(mixins.PostSerializerExtendedMixin.Meta):
        fields = mixins.PostSerializerExtendedMixin.Meta.fields + ('comments',)


class PostCreateSerializer(mixins.PostSerializerMixin):

    def create(self, validated_data):
        user = self.context['request'].user

        try:
            author = Author.objects.get(user=user)
        except ObjectDoesNotExist:
            raise serializers.ValidationError('Author does not exist')

        return Post.objects.create(author=author, **validated_data)
