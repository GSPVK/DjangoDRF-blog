from django.urls import path, include
from rest_framework import routers

from blog.api.views import comments as api_comms
from blog.api.views import posts as api_posts
from blog.api.views.categories import CategoryViewSet
from blog.views import posts, comments, common

app_name = 'blog'

urlpatterns = [
    path('index/', common.HomeView.as_view(), name='index'),
    path('all/', posts.PostListView.as_view(), name='posts'),
    path('<int:pk>/', posts.PostDetailView.as_view(), name='post-detail'),
    path('create/', posts.CreatePost.as_view(), name='create-post'),
    path('<int:pk>/edit/', posts.EditPost.as_view(), name='edit-post'),
    path('<int:pk>/delete/', posts.DeletePost.as_view(), name='delete-post'),

    path('<int:post_pk>/post-comment/', comments.CommentCreate.as_view(), name='create-comment'),
    path('<int:post_pk>/reply/<int:comment_pk>', comments.CommentCreate.as_view(), name='reply-comment'),
    path('<int:post_pk>/edit-comment/<int:comment_pk>/', comments.CommentEdit.as_view(), name='edit-comment'),
    path('<int:post_pk>/delete-comment/<int:comment_pk>/', comments.CommentDelete.as_view(), name='delete-comment'),
]

router = routers.DefaultRouter()
router.register(r'category', CategoryViewSet, 'categories')
router.register(r'post', api_posts.PostViewSet)
router.register(r'post/(?P<post_id>\d+)/comment', api_comms.CommentViewSet, 'comment')

drf_urlpatterns = [
    path('', include(router.urls)),
    path('post-with-comments/<int:pk>/', api_posts.PostWCommentsRetrieveAPIView.as_view(), name='post-with-comments'),
    path('comment/user/<int:user_id>/', api_comms.CommentListByUserAPIView.as_view(), name='comments-by-user'),
]
