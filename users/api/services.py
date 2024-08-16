from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum

from blog.api.paginators import PostPagination, CommentPagination
from blog.models import Post
from blog.pagination import paginate_and_serialize_objects

User = get_user_model()


class UserProfileService:

    @classmethod
    def add_subscription_info(cls, obj, request_user=None):
        if request_user:
            obj.user_subscribed = obj.subscribers.filter(subscriber_id=request_user.id).exists()
        else:
            obj.user_subscribed = False

    @classmethod
    def enrich_object(cls, obj, request, post_serializer=None, comment_serializer=None, request_user=None):
        """
        This method enriches the user object, including its posts and comments.
        It calculates the user's total rating, paginates and serializes the posts and comments.
        If the request_user is provided, it also checks if the request user is subscribed to the user.
        """

        comments = obj.comments.all()
        comments_rating = comments.aggregate(Sum('rating'))['rating__sum'] or 0
        try:
            # If the user is in the "Bloggers" group, they have an instance of the Author model.
            posts = obj.author.posts.all()
            posts_rating = posts.aggregate(Sum('rating'))['rating__sum'] or 0
        except ObjectDoesNotExist:
            posts = Post.objects.none()
            posts_rating = 0

        obj.total_rating = posts_rating + comments_rating

        if post_serializer:
            obj.paginated_posts = paginate_and_serialize_objects(
                objects=posts,
                paginator=PostPagination(),
                serializer=post_serializer,
                request=request
            )
        if comment_serializer:
            obj.paginated_comments = paginate_and_serialize_objects(
                objects=comments,
                paginator=CommentPagination(),
                serializer=comment_serializer,
                request=request
            )

        cls.add_subscription_info(obj, request_user)
