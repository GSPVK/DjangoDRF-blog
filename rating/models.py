from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Vote(models.Model):
    class VoteType(models.IntegerChoices):
        LIKE = 1, 'Like'
        NEUTRAL = 0, 'Neutral'
        DISLIKE = -1, 'Dislike'

    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    vote = models.IntegerField(choices=VoteType.choices)

    class Meta:
        abstract = True
        constraints = (
            models.UniqueConstraint(
                fields=['owner', 'obj'],
                name='%(class)s_unique_vote'
            ),
        )


class CommentRating(Vote):
    obj = models.ForeignKey('blog.Comment', on_delete=models.CASCADE, related_name='votes')


class PostRating(Vote):
    obj = models.ForeignKey('blog.Post', on_delete=models.CASCADE, related_name='votes')
