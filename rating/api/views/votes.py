from drf_spectacular.utils import extend_schema_view, extend_schema

from rating.api.serializers.endpoints.votes import PostVoteSerializer, CommentVoteSerializer
from rating.mixins import VoteAPIMixin
from rating.models import Vote, PostRating, CommentRating


@extend_schema_view(
    post=extend_schema(
        description="The action adds a like to a specific post identified by its `id`.",
        summary='Like a post',
        tags=['Votes']
    ),
)
class PostLikeAPIView(VoteAPIMixin):
    serializer_class = PostVoteSerializer
    rating_model = PostRating
    vote = Vote.VoteType.LIKE
    success_message = 'Post liked successfully'
    vote_removed_message = 'Like from post removed successfully'


@extend_schema_view(
    post=extend_schema(
        description="The action adds a dislike to a specific post identified by its `id`.",
        summary='Dislike a post',
        tags=['Votes']
    ),
)
class PostDislikeAPIView(VoteAPIMixin):
    serializer_class = PostVoteSerializer
    rating_model = PostRating
    vote = Vote.VoteType.DISLIKE
    success_message = 'Post disliked successfully'
    vote_removed_message = 'Dislike from post removed successfully'


@extend_schema_view(
    post=extend_schema(
        description="The action adds a like to a specific comment identified by its `id`.",
        summary='Like a comment',
        tags=['Votes']
    ),
)
class CommentLikeAPIView(VoteAPIMixin):
    serializer_class = CommentVoteSerializer
    rating_model = CommentRating
    vote = Vote.VoteType.LIKE
    success_message = 'Comment liked successfully'
    vote_removed_message = 'Like from comment removed successfully'


@extend_schema_view(
    post=extend_schema(
        description="The action adds a dislike to a specific comment identified by its `id`.",
        summary='Dislike a comment',
        tags=['Votes']
    ),
)
class CommentDislikeAPIView(VoteAPIMixin):
    serializer_class = CommentVoteSerializer
    rating_model = CommentRating
    vote = Vote.VoteType.DISLIKE
    success_message = 'Comment disliked successfully'
    vote_removed_message = 'Dislike from comment removed successfully'
