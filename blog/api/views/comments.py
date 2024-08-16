from django.db.models import Q
from django_filters.rest_framework.backends import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets, generics
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import SAFE_METHODS, AllowAny

from blog.api.serializers.endpoints import comments as comment_s
from blog.filters import IsCommentsExist, CommentFilterSet
from blog.models import Comment
from blog.pagination import CursorCreatedAtPagination
from blog.permissions import IsCommentAuthorPermission
from common.mixins.views import ExtendedView


@extend_schema_view(
    list=extend_schema(
        description="The list action returns all comments of a specific post.",
        summary='List of all comments for a specific post',
        tags=['Comment']
    ),
    retrieve=extend_schema(
        description="The retrieve action returns a single comment identified by `comment_id`.",
        summary='Retrieve a comment from a post',
        tags=['Comment']
    ),
    create=extend_schema(
        description="The create action expects the `name` field, creates a new comment in the post, and returns it.",
        summary='Leave a comment in the post',
        tags=['Comment']
    ),
    partial_update=extend_schema(
        description="The partial update action modifies specific fields of a comment identified by `comment_id`.",
        summary='Partially update a comment',
        tags=['Comment']
    ),
    update=extend_schema(
        description="The update action replaces the entire comment identified by `comment_id`.",
        summary='Fully update a comment',
        tags=['Comment']
    ),
    destroy=extend_schema(
        description="The destroy action deletes a single comment identified by `comment_id`.",
        summary='Delete a comment',
        tags=['Comment']
    ),
)
class CommentViewSet(ExtendedView, viewsets.ModelViewSet):
    # CursorPagination works well in combination with OrderingFilter
    # When trying to do sorting in CommentFilterSet (as it's done in PostFilterSet for PostViewSet) - it breaks

    queryset = Comment.objects.all()
    serializer_class = comment_s.CommentListSerializer

    permission_classes = (
        IsCommentAuthorPermission,
    )
    filter_backends = (
        IsCommentsExist,
        OrderingFilter,
        DjangoFilterBackend,
    )
    ordering = ('-created_at',)
    ordering_fields = ('id', 'rating', 'my_vote', 'created_at')
    filterset_class = CommentFilterSet

    pagination_class = CursorCreatedAtPagination
    lookup_url_kwarg = 'comment_id'

    multi_serializer_class = {
        'list': comment_s.CommentListSerializer,
        'retrieve': comment_s.CommentRetrieveSerializer,
        'create': comment_s.CommentCreateSerializer,
        'partial_update': comment_s.CommentUpdateSerializer,
        'update': comment_s.CommentUpdateSerializer,
    }

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return (AllowAny(),)
        return super().get_permissions()

    def get_queryset(self):
        queryset = Comment.objects.get_comments(
            related_args=('post', 'author',),
            request_user=self.request.user
        ).annotate(
            is_my_comment=Q(author=self.request.user)
        ).filter(
            post_id=self.kwargs.get('post_id')
        )

        return queryset


@extend_schema_view(
    get=extend_schema(
        description="Returns all comments made by a specific user, identified by their `user_id`.",
        summary='All comments by a user',
        tags=['Comment']
    ),
)
class CommentListByUserAPIView(generics.ListAPIView):
    serializer_class = comment_s.CommentListSerializer
    queryset = Comment.objects.all()
    filter_backends = (
        IsCommentsExist,
        OrderingFilter,
        DjangoFilterBackend,
    )
    ordering = ('-created_at',)
    ordering_fields = ('id', 'rating', 'my_vote', 'created_at')
    pagination_class = CursorCreatedAtPagination

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        queryset = Comment.objects.get_comments(
            related_args=('post', 'author',),
            request_user=self.request.user
        ).filter(
            author_id=user_id
        )
        return queryset
