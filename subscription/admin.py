from django.contrib import admin

from .models import UserSubscription, CategorySubscription, Favorite


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['subscriber', 'subscribed_to']
    readonly_fields = ['subscriber', 'subscribed_to']
    search_fields = ['subscriber__username']
    search_help_text = f"search in: {', '.join(search_fields)}"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('subscriber', 'subscribed_to')


@admin.register(CategorySubscription)
class CategorySubscriptionAdmin(admin.ModelAdmin):
    list_display = ['subscriber', 'subscribed_to']
    readonly_fields = ['subscriber', 'subscribed_to']
    search_fields = ['subscriber__username', 'subscribed_to__title']
    search_help_text = f"search in: {', '.join(search_fields)}"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('subscriber', 'subscribed_to')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'post']
    readonly_fields = ['user', 'post']
    search_fields = ['user__username', 'post__title']
    search_help_text = f"search in: {', '.join(search_fields)}"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'post')
