from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView

from blog.mixins import views as blogmixins
from blog.models import Post, Comment


class CommentCreate(LoginRequiredMixin, CreateView):
    model = Comment
    fields = ('text',)
    queryset = Post.objects.all()
    pk_url_kwarg = 'post_pk'

    def get_queryset(self):
        return Post.objects.filter(pk=self.kwargs['post_pk'])

    def form_valid(self, form):
        author = self.request.user
        post = self.get_object()
        if self.kwargs.get('comment_pk'):
            form.instance.reply_to = post.comments.filter(pk=self.kwargs['comment_pk']).first()
        form.instance.author = author
        form.instance.post = post
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        if self.kwargs.get('comment_pk'):
            context['comment'] = post.comments.filter(pk=self.kwargs['comment_pk']).select_related(
                'author__profile').first()
            context['is_reply'] = True
        context['post'] = post
        return context

    def get_success_url(self):
        return reverse_lazy('blog:post-detail', kwargs={'pk': self.kwargs['post_pk']})


class CommentEdit(blogmixins.CommentLoginRequiredAndCheckAuthorMixin, UpdateView):
    model = Comment
    fields = ('text',)
    pk_url_kwarg = 'comment_pk'

    def get_success_url(self):
        return reverse_lazy('blog:post-detail', kwargs={'pk': self.kwargs['post_pk']})


class CommentDelete(blogmixins.CommentLoginRequiredAndCheckAuthorMixin, DeleteView):
    model = Comment
    pk_url_kwarg = 'comment_pk'

    def get_success_url(self):
        return reverse_lazy('blog:post-detail', kwargs={'pk': self.kwargs['post_pk']})
