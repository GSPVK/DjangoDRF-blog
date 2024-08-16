from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, get_object_or_404

from blog.models import Comment, Post
from .models import PostRating, CommentRating, Vote

User = get_user_model()


def change_vote(user, rating_model, pk, vote_type):
    """
    Change or set a vote for a given rating object

    This function attempts to change the vote (like, dislike, neutral) associated with a model instance
    based on the user's input. If the vote type provided is invalid, it returns an HttpResponseBadRequest.
    Otherwise, it updates or creates a vote record in a transaction-safe way.
    """
    new_vote = Vote.VoteType[vote_type]

    vote_obj = rating_model.objects.filter(obj_id=pk, owner_id=user.id).first()

    if not vote_obj:
        vote_obj = rating_model(obj_id=pk, owner_id=user.id, vote=new_vote)
    elif vote_obj.vote != new_vote.value:
        vote_obj.vote = new_vote
    else:  # If the existing vote is equal to the vote entered by the user - make it neutral.
        vote_obj.vote = Vote.VoteType.NEUTRAL
    vote_obj.save()


@login_required
def change_rating(request, post_pk, vote_type, comm_pk=None):
    if vote_type not in Vote.VoteType.names:
        return HttpResponseBadRequest('Invalid vote type')

    if post_pk and comm_pk:
        get_object_or_404(Comment, pk=comm_pk)
        change_vote(request.user, CommentRating, comm_pk, vote_type=vote_type)
    elif post_pk:
        get_object_or_404(Post, pk=post_pk)
        change_vote(request.user, PostRating, post_pk, vote_type=vote_type)
    else:
        return HttpResponseBadRequest()

    next_page = request.GET.get('next', '/')
    return redirect(next_page)
