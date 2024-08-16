from django.urls import path

from subscription.views import subscriptions, favorites, feed
from subscription.api.views import favorites as api_favorites
from subscription.api.views import feed as api_feed
from subscription.api.views import subscriptions as api_subs

app_name = 'subscription'

urlpatterns = [
    path('my/', feed.FeedListView.as_view(), name='my-feed'),
    path('my-subscription/', subscriptions.MySubscriptionsListView.as_view(), name='my-subscriptions'),
    path('change-subscription/<str:object_type>/<int:object_id>/<str:action>/',
         subscriptions.ChangeSubscriptionView.as_view(),
         name='change-subscription'),

    path('my-favorites/', favorites.FavoritesView.as_view(), name='my-favorites'),
    path('change-favorite/<int:post_id>/<str:action>/',
         favorites.ChangeFavoriteView.as_view(),
         name='change-favorite'),
]

drf_urlpatterns = [
    path('my_favorites/', api_favorites.MyFavoritesAPIView.as_view(), name='my-favorites'),
    path('post/<int:pk>/add-favorite/', api_favorites.AddFavoriteAPIView.as_view(), name='add-favorite'),
    path('post/<int:pk>/remove-favorite/', api_favorites.RemoveFavoriteAPIView.as_view(), name='remove-favorite'),
    path('my-feed/', api_feed.MyFeedAPIView.as_view(), name='my-feed'),
    path('my-subscriptions/users/', api_subs.MyUserSubscriptionsAPIView.as_view(), name='my-user-subscriptions'),
    path('my-subscriptions/categories/', api_subs.MyCategoriesSubscriptionsAPIView.as_view(), name='my-categories-subscriptions'),
    path('user/<int:pk>/subscribe/', api_subs.UserSubscribeAPIView.as_view(), name='user-subscribe'),
    path('user/<int:pk>/unsubscribe/', api_subs.UserUnsubscribeAPIView.as_view(), name='user-unsubscribe'),
    path('category/<int:pk>/subscribe/', api_subs.CategorySubscribeAPIView.as_view(), name='category-subscribe'),
    path('category/<int:pk>/unsubscribe/', api_subs.CategoryUnsubscribeAPIView.as_view(), name='category-unsubscribe'),
]
