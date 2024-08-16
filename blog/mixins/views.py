from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Prefetch

from blog.models import Post, Comment, Author


class PostDetailQuerySetMixin:
    def get_queryset(self):
        comments_prefetch = Prefetch('comments', Comment.objects.get_comments(
            related_args=['author__profile'],
            request_user=self.request.user
        ))

        qs = Post.objects.select_related(
            'author__user__profile',
            'category',
        ).prefetch_related(
            'favorites',
            comments_prefetch
        ).annotate(
            rating=Post.objects.get_rating_subquery(),
        )

        if self.request.user.is_authenticated:
            qs = Post.objects.get_user_annotate(self.request.user, qs)

        return qs


class PostLoginRequiredAndGetAuthorMixin(AccessMixin):

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        try:
            self.author = Author.objects.get(user=self.request.user)
        except Author.DoesNotExist:
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)


class PostLoginRequiredAndCheckAuthorMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        # check if the user is the author of the post or is staff
        self.object = self.get_object()
        if self.object.author.user != request.user and not request.user.is_staff:
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)


class CommentLoginRequiredAndCheckAuthorMixin(AccessMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        # check if the user is the author of the post or is staff
        self.object = self.get_object()
        if self.object.author != request.user and not request.user.is_staff:
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)
