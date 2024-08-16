from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Prefetch, Sum
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView

from blog.models import Post, Comment
from users.forms import CreationForm, UserProfileForm

User = get_user_model()


class UserProfileView(DetailView):
    model = User
    context_object_name = 'profile'

    def _paginate_objects(self, objects, paginate_by, url_kwarg):
        paginator = Paginator(objects, paginate_by)
        page = self.request.GET.get(url_kwarg, 1)
        return paginator.get_page(page)

    def get_queryset(self):
        comments_prefetch = Prefetch('comments', Comment.objects.get_comments(request_user=self.request.user))
        posts_prefetch = Post.objects.get_posts_prefetch(request_user=self.request.user)

        return User.objects.select_related(
            'author',
            'profile',
        ).prefetch_related(
            comments_prefetch,
            posts_prefetch
        )

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)

        request_user = self.request.user

        comments = obj.comments.all()
        comments_rating = comments.aggregate(Sum('rating'))['rating__sum'] or 0
        try:
            # If the user is in the "Bloggers" group, they have an instance of the Author model.
            posts = obj.author.posts.all()
            posts_rating = posts.aggregate(Sum('rating'))['rating__sum'] or 0
        except ObjectDoesNotExist:
            posts = Post.objects.none()
            posts_rating = 0

        self.rating = comments_rating + posts_rating

        obj.paginated_comments = self._paginate_objects(
            objects=comments,
            paginate_by=5,
            url_kwarg='comments_page'
        )
        obj.paginated_posts = self._paginate_objects(
            objects=posts,
            paginate_by=2,
            url_kwarg='posts_page'
        )

        obj.user_subscribed = obj.subscribers.filter(subscriber_id=request_user.id)

        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({
            'posts': self.object.paginated_posts,
            'comments': self.object.paginated_comments,
            'rating': self.rating,
            'subscribed': self.object.user_subscribed,
        })

        return context


class UserProfileEditView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'users/user_form.html'

    def get_object(self, *args, **kwargs):
        obj = super().get_object(*args, **kwargs)
        if obj != self.request.user:
            raise PermissionDenied()
        return obj

    def get_queryset(self):
        return User.objects.select_related('profile')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request

        return kwargs


class SignUpView(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/sign_up.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('blog:index')
        return super().dispatch(request, *args, **kwargs)
