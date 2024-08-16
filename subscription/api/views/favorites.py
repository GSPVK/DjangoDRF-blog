from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from blog.api.serializers.endpoints import posts as post_s
from blog.filters import PostFilterSet
from blog.models import Post
from subscription.api.serializers.endpoints.favorites import FavoriteSerializer
from subscription.models import Favorite


@extend_schema_view(
    post=extend_schema(
        description="The action adds a specific post identified by its `id` to the user's favorites.",
        summary='Add a post to favorites',
        tags=['Favorites']
    ),
)
class AddFavoriteAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = FavoriteSerializer

    def post(self, request, *args, **kwargs):
        user = request.user
        post_id = self.kwargs.get('pk')
        post = get_object_or_404(Post, pk=post_id)

        try:
            Favorite.objects.get(user=user, post_id=post.pk)
            return Response(data={'success': 'Post already in favorites.'}, status=status.HTTP_409_CONFLICT)
        except Favorite.DoesNotExist:
            Favorite.objects.create(user=user, post_id=post.pk)

        return Response(data={'success': 'Post added to favorites!'}, status=status.HTTP_201_CREATED)


@extend_schema_view(
    post=extend_schema(
        description="The action removes a specific post identified by its `id` from the user's favorites.",
        summary='Remove a post from favorites',
        tags=['Favorites']
    ),
)
class RemoveFavoriteAPIView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = FavoriteSerializer

    def post(self, request, *args, **kwargs):
        user = request.user
        post_id = self.kwargs.get('pk')

        favorite = get_object_or_404(Favorite, user=user, post_id=post_id)
        favorite.delete()

        return Response(data={'success': 'Post removed from favorites!'}, status=status.HTTP_200_OK)


@extend_schema_view(
    get=extend_schema(
        description="Returns a list of posts that the current user has added to their favorites.",
        summary='My favorite posts',
        tags=['Favorites']
    ),
)
class MyFavoritesAPIView(ListAPIView):
    queryset = Post.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = post_s.PostSerializer
    filter_backends = (
        DjangoFilterBackend,
    )
    filterset_class = PostFilterSet

    def get_queryset(self):
        user = self.request.user
        return Post.objects.get_posts_list(user=user).filter(favorites__user=user)
