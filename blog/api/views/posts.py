from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, AllowAny

from blog.api.paginators import CommentPagination
from blog.api.serializers.endpoints import posts as posts_s
from blog.api.serializers.endpoints.comments import CommentListSerializer
from blog.filters import PostFilterSet
from blog.mixins.views import PostDetailQuerySetMixin
from blog.models import Post
from blog.pagination import paginate_and_serialize_objects
from blog.permissions import IsPostAuthorPermission, IsBloggerPermission
from common.mixins.views import ExtendedView


@extend_schema_view(
    get=extend_schema(
        description="The retrieve action returns a single post identified by `id`, including paginated comments.",
        summary='Full post details (with paginated comments)',
        tags=['Post']
    ),
)
class PostWCommentsRetrieveAPIView(PostDetailQuerySetMixin, generics.RetrieveAPIView):
    queryset = Post.objects.all().select_related('author__user')
    serializer_class = posts_s.PostRetrieveWithCommentsSerializer
    filter_backends = (
        DjangoFilterBackend,
    )
    filterset_class = PostFilterSet

    def get_object(self):
        self.object = super().get_object()
        comments = self.object.comments.all()

        self.object.paginated_comments = paginate_and_serialize_objects(
            objects=comments,
            paginator=CommentPagination(),
            serializer=CommentListSerializer,
            request=self.request
        )

        return self.object

    def get_serializer_context(self):
        context = super().get_serializer_context()

        context.update({
            'comments': self.object.paginated_comments
        })

        return context


@extend_schema_view(
    list=extend_schema(
        description="The list action returns all available posts.",
        summary='List of posts',
        tags=['Post']
    ),
    create=extend_schema(
        description="The create action expects the `name` field, creates a new post, and returns it.",
        summary='Create a post',
        tags=['Post']
    ),
    retrieve=extend_schema(
        description="The retrieve action returns a single post identified by `id`.",
        summary='Post details',
        tags=['Post']
    ),
    partial_update=extend_schema(
        description="The partial update action modifies specific fields of a post identified by `id`.",
        summary='Partially update a post',
        tags=['Post']
    ),
    update=extend_schema(
        description="The update action replaces the entire post identified by `id`.",
        summary='Fully update a post',
        tags=['Post']
    ),
    destroy=extend_schema(
        description="The destroy action deletes a single post identified by `id`.",
        summary='Delete a post',
        tags=['Post']
    ),
    posts_by_author=extend_schema(
        description="Returns all posts authored by a specific user, identified by their `author_id`.",
        summary='All posts by an author',
        tags=['Post']
    ),
)
class PostViewSet(ExtendedView, viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = posts_s.PostSerializer

    permission_classes = (
        IsPostAuthorPermission,
        IsBloggerPermission
    )
    filter_backends = (
        DjangoFilterBackend,
    )
    filterset_class = PostFilterSet

    multi_serializer_class = {
        'list': posts_s.PostSerializer,
        'create': posts_s.PostCreateSerializer,
    }

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return (AllowAny(),)
        return super().get_permissions()

    def get_queryset(self):
        queryset = Post.objects.get_posts_list(user=self.request.user)
        if self.action == 'posts_by_author':
            user_id = self.kwargs.get('user_id')
            queryset = queryset.filter(author__user_id=user_id)
        return queryset

    @action(methods=['get'], detail=False, url_path=r'by_author/(?P<user_id>\d+)', url_name='author-posts')
    def posts_by_author(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
