from django.contrib.auth import get_user_model
from django.db.models import Prefetch
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT

from blog.api.serializers.endpoints import comments as comments_s
from blog.api.serializers.endpoints import posts as post_s
from blog.models import Comment, Post
from users.api.serializers.endpoints import users as user_s
from users.api.serializers.nested import profile as profile_s
from users.api.services import UserProfileService

User = get_user_model()


@extend_schema_view(
    post=extend_schema(
        description="Allows a new user to create an account by providing necessary information.",
        summary='Sign up',
        tags=['Authentication & Authorization']
    ),
)
class SignUpAPIView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    queryset = User.objects.all()
    serializer_class = user_s.SignUpSerializer


@extend_schema_view(
    put=extend_schema(
        description="Allows the authenticated user to change their password by providing the `old password` and the `new password`.",
        summary='Change password',
        tags=['Authentication & Authorization']
    ),
)
class ChangePasswordAPIView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = user_s.ChangePasswordSerializer

    def put(self, request, *args, **kwargs):
        user = request.user
        serializer = user_s.ChangePasswordSerializer(instance=user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=HTTP_204_NO_CONTENT)


@extend_schema_view(
    get=extend_schema(
        description="Retrieves the profile of the currently authenticated user, including basic information.",
        summary='View my profile (brief)',
        tags=['User profile']
    ),
    patch=extend_schema(
        description="Updates specific fields of the authenticated user's profile.",
        summary='Edit my profile',
        tags=['User profile']
    ),
    put=extend_schema(
        description="Replaces the entire profile information of the authenticated user with the new provided values.",
        summary='Replace my profile',
        tags=['User profile']
    ),
)
class MeAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = User.objects.all()
    serializer_class = user_s.MeSerializer

    def get_queryset(self):
        return User.objects.select_related(
            'author',
            'profile',
        ).prefetch_related(
            'subscribers',
        )

    def get_object(self):
        return self.get_queryset().get(pk=self.request.user.pk)


@extend_schema_view(
    get=extend_schema(
        description="Retrieves the complete profile of the authenticated user, including posts, comments, and their rating.",
        summary='View my full profile (with posts and comments)',
        tags=['User profile']
    ),
)
class FullMeAPIView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = User.objects.all()
    serializer_class = user_s.FullMeSerializer

    def get_queryset(self):
        comments_prefetch = Prefetch('comments', Comment.objects.get_comments())
        posts_prefetch = Post.objects.get_posts_prefetch(request_user=self.request.user)

        return User.objects.select_related(
            'author',
            'profile',
        ).prefetch_related(
            'subscribers',
            comments_prefetch,
            posts_prefetch
        )

    def get_object(self):
        self.object = self.get_queryset().get(pk=self.request.user.pk)

        UserProfileService.enrich_object(
            obj=self.object,
            post_serializer=profile_s.MyPostsListSerializer,
            comment_serializer=profile_s.MyCommentsListSerializer,
            request=self.request,
        )

        return self.object

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({
            'posts': self.object.paginated_posts,
            'comments': self.object.paginated_comments
        })
        return context


@extend_schema_view(
    get=extend_schema(
        description="Retrieves a brief profile of a user by their `ID`, excluding detailed information like posts, comments, and rating.",
        summary='View user profile by ID (brief)',
        tags=['User profile']
    ),
)
class UserProfileAPIView(generics.RetrieveAPIView):
    queryset = User.objects
    serializer_class = user_s.UserProfileSerializer

    def get_queryset(self):
        return User.objects.select_related(
            'author',
            'profile',
        )

    def get_object(self):
        self.object = super().get_object()

        if self.request.user:
            UserProfileService.add_subscription_info(self.object, self.request.user)

        return self.object


@extend_schema_view(
    get=extend_schema(
        description="Retrieves a detailed profile of a user by their `ID`, including their posts and comments.",
        summary='View user profile by ID (with their posts and comments)',
        tags=['User profile']
    ),
)
class FullUserProfileAPIView(generics.RetrieveAPIView):
    queryset = User.objects
    serializer_class = user_s.FullUserProfileSerializer

    def get_queryset(self):
        comm_prefetch_kwargs = {}
        if self.request.user.is_authenticated:
            comm_prefetch_kwargs = {'request_user': self.request.user}
        comments_prefetch = Prefetch('comments', Comment.objects.get_comments(**comm_prefetch_kwargs))

        posts_prefetch = Post.objects.get_posts_prefetch(request_user=self.request.user)

        return User.objects.select_related(
            'author',
            'profile',
        ).prefetch_related(
            comments_prefetch,
            posts_prefetch
        )

    def get_object(self):
        self.object = super().get_object()
        get_object_kwargs = {
            'obj': self.object,
            'post_serializer': post_s.PostSerializer,
            'comment_serializer': comments_s.CommentListSerializer,
            'request': self.request,
        }

        if self.request.user.is_authenticated:
            get_object_kwargs['request_user'] = self.request.user

        UserProfileService.enrich_object(**get_object_kwargs)

        return self.object

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({
            'posts': self.object.paginated_posts,
            'comments': self.object.paginated_comments
        })
        return context
