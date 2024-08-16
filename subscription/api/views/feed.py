from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from blog.api.serializers.endpoints import posts as post_s
from blog.filters import PostFilterSet
from blog.models import Post


@extend_schema_view(
    get=extend_schema(
        description="Returns a personalized feed with posts from users/categories the current user is subscribed to.",
        summary='My feed',
        tags=['Subscriptions']
    ),
)
class MyFeedAPIView(generics.ListAPIView):
    queryset = Post.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = post_s.PostSerializer
    filter_backends = (
        DjangoFilterBackend,
    )
    filterset_class = PostFilterSet

    def get_queryset(self):
        user = self.request.user
        return Post.objects.get_user_feed(user=user)
