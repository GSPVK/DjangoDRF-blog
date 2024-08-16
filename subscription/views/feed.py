from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django_filters.views import FilterView

from blog.filters import PostFilterSet
from blog.models import Post

User = get_user_model()


class FeedListView(LoginRequiredMixin, FilterView):
    model = Post
    paginate_by = 10
    template_name = 'subscription/feed.html'
    filterset_class = PostFilterSet

    def get_queryset(self):
        user = self.request.user
        return Post.objects.get_user_feed(user=user)
