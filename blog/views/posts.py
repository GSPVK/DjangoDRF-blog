from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView
from django_filters.views import FilterView

from blog.filters import PostFilterSet
from blog.mixins import views as blogmixins
from blog.models import Post, Category
from common.mixins.views import CommentTreeMixin


class PostListView(FilterView):
    model = Post
    paginate_by = 5
    template_name = 'blog/post_list.html'
    filterset_class = PostFilterSet

    def get_queryset(self):
        return Post.objects.get_posts_list(user=self.request.user)

    def _update_context_with_category_information(self, category, context):
        """
        Add information about the selected category to the context.
        """
        category_obj = get_object_or_404(Category, title=category)
        category_subscribers = category_obj.subscribers.values_list('subscriber_id', flat=True)

        context.update({
            'category': category_obj,
            'subscribed': self.request.user.pk in category_subscribers,
            'subscribers_count': category_subscribers.count(),
        })

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=None, **kwargs)

        category = self.request.GET.get('category')
        if category:
            self._update_context_with_category_information(category, context)

        context['header'] = category or 'All posts'

        return context


class PostDetailView(blogmixins.PostDetailQuerySetMixin, CommentTreeMixin, DetailView):
    model = Post
    root_comments_paginate_by = 5
    comment_replies_limit = 3

    def get_object(self, queryset=None):
        obj = super().get_object()

        comments = obj.comments.all()
        comment_tree = self.comment_tree(comments)
        paginator = Paginator(comment_tree, self.root_comments_paginate_by)

        page_number = self.request.GET.get('page')
        obj.page_obj = paginator.get_page(page_number)  # ?

        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['page_obj'] = self.object.page_obj

        return context


class CreatePost(blogmixins.PostLoginRequiredAndGetAuthorMixin, CreateView):
    model = Post
    fields = ['title', 'category', 'text']
    success_url = reverse_lazy('blog:posts')

    def form_valid(self, form):
        form.instance.author = self.author
        return super().form_valid(form)


class EditPost(blogmixins.PostLoginRequiredAndCheckAuthorMixin, UpdateView):
    model = Post
    fields = ['title', 'category', 'text']

    def get_success_url(self):
        return reverse_lazy('blog:post-detail', kwargs={'pk': self.kwargs['pk']})


class DeletePost(blogmixins.PostLoginRequiredAndCheckAuthorMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('blog:posts')
