from typing import Optional, List

from django.core.exceptions import ObjectDoesNotExist
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from blog.api.serializers.endpoints.comments import CommentListSerializer
from blog.api.serializers.endpoints.posts import PostSerializer
from blog.api.serializers.nested.comments import PaginatedCommentsSerializer
from blog.api.serializers.nested.posts import PaginatedPostsSerializer
from blog.models import User
from users.models import Profile


class ProfileShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = (
            'telegram_id',
            'photo'
        )


class ProfileSerializerMixin(serializers.ModelSerializer):
    profile = ProfileShortSerializer()
    biography = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'date_joined',
            'first_name',
            'last_name',
            'biography',
            'email',
            'phone_number',
            'username',
            'profile',
            'subscribers_count',
        )
        read_only_fields = ('date_joined', 'username', 'subscribers_count',)

    @extend_schema_field(serializers.CharField)
    def get_biography(self, obj) -> Optional[str]:
        try:
            # If the user is in the "Bloggers" group, they have an instance of the Author model.
            return obj.author.bio
        except ObjectDoesNotExist:
            ...
        return None


class ProfileExtendedSerializerMixin(ProfileSerializerMixin):
    rating = serializers.IntegerField(source='total_rating')
    posts = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()

    class Meta(ProfileSerializerMixin.Meta):
        fields = ProfileSerializerMixin.Meta.fields + ('rating', 'posts', 'comments',)

    @extend_schema_field(PaginatedPostsSerializer)
    def get_posts(self, obj) -> Optional[List[PostSerializer]]:
        return self.context.get('posts')

    @extend_schema_field(PaginatedCommentsSerializer)
    def get_comments(self, obj) -> Optional[List[CommentListSerializer]]:
        return self.context.get('comments')
