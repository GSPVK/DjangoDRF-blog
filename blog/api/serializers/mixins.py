from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from blog.models import Post, Category, Comment

User = get_user_model()


class PostSerializerMixin(serializers.HyperlinkedModelSerializer):
    author = serializers.StringRelatedField()
    author_profile = serializers.HyperlinkedRelatedField(
        source='author.user',
        view_name='users:profile',
        read_only=True
    )
    url = serializers.HyperlinkedIdentityField(view_name='blog:post-detail')
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='title'
    )
    rating = serializers.IntegerField(read_only=True)
    fav_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Post
        fields = (
            'id',
            'created_at',
            'updated_at',
            'title',
            'url',
            'author',
            'author_profile',
            'category',
            'text',
            'rating',
            'fav_count',
            'comments_count',
        )
        read_only_fields = (
            'created_at',
            'updated_at',
        )


class PostSerializerExtendedMixin(PostSerializerMixin):
    # my_favorite and my_vote are taken from the custom manager of the Post model
    my_favorite = serializers.SerializerMethodField()
    my_vote = serializers.SerializerMethodField()

    class Meta(PostSerializerMixin.Meta):
        fields = PostSerializerMixin.Meta.fields + ('my_favorite', 'my_vote',)

    @extend_schema_field(serializers.BooleanField)
    def get_my_favorite(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.user_favorite
        return None

    @extend_schema_field(serializers.IntegerField)
    def get_my_vote(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.user_vote
        return None


class CommentsSerializerMixin(serializers.ModelSerializer):
    author = serializers.StringRelatedField()
    post_title = serializers.StringRelatedField(source='post')
    post_url = serializers.HyperlinkedRelatedField(
        view_name='blog:post-detail',
        source='post',
        read_only=True
    )
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Comment
        fields = (
            'id',
            'author',
            'post_title',
            'post_url',
            'reply_to',
            'text',
            'rating'
        )


class CommentsSerializerExtendedMixin(CommentsSerializerMixin):
    my_vote = serializers.SerializerMethodField()

    class Meta(CommentsSerializerMixin.Meta):
        fields = CommentsSerializerMixin.Meta.fields + ('my_vote',)

    @extend_schema_field(serializers.IntegerField)
    def get_my_vote(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.user_vote
        return None


class CategorySerializerMixin(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'title',)
