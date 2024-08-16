from django.urls import path

from . import views
from rating.api.views import votes as api_vote

app_name = 'rating'

urlpatterns = [
    path('<int:post_pk>/vote/<str:vote_type>', views.change_rating, name='post-rating'),
    path('<int:post_pk>/vote/<int:comm_pk>/<str:vote_type>', views.change_rating, name='comment-rating'),
]

drf_urlpatterns = [
    path('post/<int:pk>/like', api_vote.PostLikeAPIView.as_view(), name='post-like'),
    path('post/<int:pk>/dislike', api_vote.PostDislikeAPIView.as_view(), name='post-dislike'),
    path('comment/<int:pk>/like', api_vote.CommentLikeAPIView.as_view(), name='comment-like'),
    path('comment/<int:pk>/dislike', api_vote.CommentDislikeAPIView.as_view(), name='comment-dislike'),
]
