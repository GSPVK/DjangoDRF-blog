from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from common.mixins.admin import ExtendedModelAdmin
from rating.models import CommentRating, PostRating
from .models import Author, Post, Comment, Category


@admin.register(Author)
class AuthorAdmin(ExtendedModelAdmin):
    list_display = ['id', 'user', 'posts_total']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user').prefetch_related('posts')

    def get_object_queryset(self, request):
        return super().get_queryset(request).select_related('user')

    def posts_total(self, obj):
        return obj.posts.count()


@admin.register(Category)
class CategoryAdmin(ExtendedModelAdmin):
    list_display = ['id', 'title', 'posts_total']
    search_fields = ['title', ]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('posts')

    def get_object_queryset(self, request):
        return super().get_queryset(request)

    def posts_total(self, obj):
        return obj.posts.count()


class PostRatingInline(admin.TabularInline):
    readonly_fields = ['owner']
    model = PostRating
    extra = 0


@admin.register(Post)
class PostAdmin(ExtendedModelAdmin):
    list_display = ['id', 'title', 'author', 'category', 'rating', 'fav_count', 'comments_count', 'created_at']
    inlines = [PostRatingInline]
    readonly_fields = ['author', 'created_at', 'updated_at', ]
    autocomplete_fields = ['category', ]
    search_fields = ['title', ]

    def get_queryset(self, request):
        rating_subq = Post.objects.get_rating_subquery()
        return super().get_queryset(request).select_related(
            'author__user',
            'category',
        ).prefetch_related(
            'favorites',
            'comments'
        ).annotate(
            rating=rating_subq)

    def get_object_queryset(self, request):
        return super().get_queryset(request).select_related(
            'author__user',
            'category',
        )

    def rating(self, obj):
        return obj.rating

    def fav_count(self, obj):
        return obj.fav_count

    def comments_count(self, obj):
        return obj.comments_count


class CommentRatingInline(admin.TabularInline):
    readonly_fields = ['owner', 'vote']
    model = CommentRating
    extra = 0


@admin.register(Comment)
class CommentAdmin(ExtendedModelAdmin):
    list_display = ['id', 'short_text', 'author', 'post_link', 'rating', 'created_at']
    readonly_fields = ['author', 'post', 'reply_to', 'created_at', 'updated_at', ]
    inlines = [CommentRatingInline]

    def get_queryset(self, request):
        rating_subq = Comment.objects.get_rating_subquery()

        return super().get_queryset(request).select_related(
            'post', 'author'
        ).annotate(
            rating=rating_subq,
        )

    def get_object_queryset(self, request):
        return super().get_queryset(request).select_related(
            'post', 'author'
        )

    def rating(self, obj):
        return obj.rating

    def post_link(self, obj):
        link = reverse('admin:blog_post_change', args=[obj.post.pk])
        return format_html('<a href="{}">{}</a>', link, obj.post)

    def short_text(self, obj):
        return obj.__str__()

    short_text.short_description = 'Text'
    post_link.short_description = 'Post'
