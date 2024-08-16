from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django_filters.views import FilterView

from blog.filters import PostFilterSet
from blog.models import Post
from subscription.models import Favorite


class FavoritesView(LoginRequiredMixin, FilterView):
    model = Post
    paginate_by = 10
    template_name = 'subscription/favorites.html'
    filterset_class = PostFilterSet

    def get_queryset(self):
        user = self.request.user
        return Post.objects.get_posts_list(user=user).filter(favorites__user=user)


class ChangeFavoriteView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        user = request.user
        post_id = self.kwargs.get('post_id')
        action = self.kwargs.get('action')

        if action == 'add':
            post = get_object_or_404(Post, pk=post_id)
            Favorite.objects.get_or_create(user=user, post_id=post.pk)
        elif action == 'remove':
            favorite = get_object_or_404(Favorite, user=user, post_id=post_id)
            favorite.delete()
        else:
            return HttpResponseBadRequest('Invalid action')

        next_page = request.GET.get('next', '/')
        return redirect(next_page)
