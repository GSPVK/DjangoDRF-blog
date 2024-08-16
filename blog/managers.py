from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Subquery, Sum, OuterRef, Prefetch, Exists, Value, IntegerField, Q
from django.db.models.functions import Coalesce

from rating.models import PostRating, CommentRating
from subscription.models import Favorite

User = get_user_model()


class PostManager(models.Manager):
    def get_rating_subquery(self):
        """
        Returns a subquery to calculate the overall rating of a post.
        """
        subquery = PostRating.objects.filter(
            obj_id=OuterRef('pk'),
        ).values(
            'obj_id'
        ).annotate(
            post_rating=Sum('vote')
        ).values(
            'post_rating'
        )

        return Coalesce(Subquery(subquery, output_field=IntegerField()), Value(0))

    def get_posts_prefetch(self, request_user=None):
        posts = self.select_related(
            'category',
        ).prefetch_related(
            'comments',
            'favorites',
        ).annotate(
            rating=self.get_rating_subquery(),
        )

        if request_user and request_user.is_authenticated:
            posts = self.get_user_annotate(request_user, posts)

        return Prefetch('author__posts', posts)

    def get_user_annotate(self, user, queryset):
        """
        Annotate posts with additional data related to the current user.

        - favorite: whether the current user has marked the post as favorite
        - user_vote: the vote given by the current user to the post, if any
        """
        user_favorite_subquery = Favorite.objects.filter(
            post=OuterRef('pk'),
            user=user
        )

        user_vote_subquery = PostRating.objects.filter(
            obj_id=OuterRef('pk'),
            owner_id=user.pk
        ).values('vote')[:1]

        return queryset.annotate(
            user_favorite=Exists(user_favorite_subquery),
            user_vote=Coalesce(Subquery(user_vote_subquery), 0)
        )

    def get_posts_list(self, user=None):
        """
        Retrieves a list of posts.
        Applies user-specific annotations if a user is provided.
        """
        queryset = self.select_related(
            'author__user__profile',
            'category',
        ).prefetch_related(
            'comments',
            'favorites',
        ).annotate(
            rating=self.get_rating_subquery(),
        )

        if user and user.is_authenticated:
            queryset = self.get_user_annotate(user, queryset)

        return queryset

    def get_user_feed(self, user):
        subbed_categories = user.category_subscriptions.values_list('subscribed_to', flat=True)
        subbed_users = user.user_subscriptions.values_list('subscribed_to', flat=True)

        return self.get_posts_list(user=user).filter(
            Q(category_id__in=subbed_categories) | Q(author__user_id__in=subbed_users)
        )


class CommentManager(models.Manager):
    def get_rating_subquery(self):
        """
        Returns a subquery to calculate the overall rating of a comment.
        """
        subquery = CommentRating.objects.filter(
            obj_id=OuterRef('pk')
        ).values(
            'obj_id'
        ).annotate(
            comment_rating=Sum('vote')
        ).values(
            'comment_rating'
        )

        return Coalesce(Subquery(subquery, output_field=IntegerField()), Value(0))

    def get_user_annotate(self, user, queryset):
        """
        Annotate comments with additional data related to the current user.

        - user_vote: the vote given by the current user to the comment, if any
        """
        return queryset.annotate(
            user_vote=Coalesce(
                Subquery(
                    CommentRating.objects.filter(
                        obj_id=OuterRef('id'),
                        owner_id=user.pk
                    ).values('vote')[:1]
                ), 0
            )
        )

    def get_comments(self, related_args=None, request_user: User = None):
        if not related_args:
            related_args = (
                'post',
            )
        comments_qs = self.select_related(
            *related_args,
        ).annotate(
            rating=self.get_rating_subquery(),
        )

        if request_user and request_user.is_authenticated:
            comments_qs = self.get_user_annotate(user=request_user, queryset=comments_qs)

        return comments_qs
