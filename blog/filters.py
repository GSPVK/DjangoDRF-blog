import django_filters
from django.core.cache import cache
from rest_framework.exceptions import NotFound
from rest_framework.filters import BaseFilterBackend

from blog import constants as const
from blog.models import Comment
from blog.models import Post, Category


class PostFilterSet(django_filters.FilterSet):
    class Meta:
        model = Post
        fields = ('category', 'ordering')

    ordering_choices = (
        ('rating', 'Low rated'),
        ('-rating', 'Top rated'),
        ('created_at', 'Older'),
        ('-created_at', 'Newer'),
    )

    ordering = django_filters.OrderingFilter(
        fields=('rating', 'created_at'),
        choices=ordering_choices,
        field_labels={'rating': 'Rating', 'created_at': 'Created'},
    )

    category = django_filters.ChoiceFilter(
        field_name='category__title',
        label='Category',
        choices=[]
    )

    def __init__(self, *args, **kwargs):
        """
        Initializes the PostFilterSet instance and dynamically sets the category choices.
        """
        super().__init__(*args, **kwargs)

        cached_choices = cache.get(const.CATEGORY_CACHE_KEY)
        if cached_choices is None:
            cached_choices = [
                (category.title, category.title) for category in Category.objects.all()
            ]
            cache.set(const.CATEGORY_CACHE_KEY, cached_choices)

        self.filters['category'].extra['choices'] = cached_choices


class IsCommentsExist(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if not queryset.exists():
            raise NotFound('Comments not found')
        return queryset


class CommentFilterSet(django_filters.FilterSet):
    is_my_comment = django_filters.BooleanFilter(label='Show my comments only')

    class Meta:
        model = Comment
        fields = ('is_my_comment',)
