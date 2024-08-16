from django.shortcuts import get_object_or_404

from blog.api.serializers import mixins
from blog.models import Comment, Post
from common.mixins import serializers as common_s


class CommentListSerializer(common_s.TruncateTextSerializer, mixins.CommentsSerializerExtendedMixin):
    ...


class CommentRetrieveSerializer(mixins.CommentsSerializerExtendedMixin):
    ...


class CommentCreateSerializer(mixins.CommentsSerializerMixin):
    class Meta:
        model = Comment
        fields = ('text', 'reply_to')

    def validate(self, attrs):
        user = self.context['request'].user
        attrs['author'] = user
        post_id = self.context['view'].kwargs.get('post_id')
        post = get_object_or_404(Post, pk=post_id)
        attrs['post'] = post
        return super().validate(attrs)


class CommentUpdateSerializer(mixins.CommentsSerializerMixin):
    class Meta:
        model = Comment
        fields = ('text',)
