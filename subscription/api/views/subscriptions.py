from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from blog.models import Category
from subscription.api.serializers.endpoints import subscriptions as sub_s
from subscription.mixins import SubscriptionMixin
from subscription.models import UserSubscription, CategorySubscription

User = get_user_model()


@extend_schema_view(
    post=extend_schema(
        description="Allows the authenticated user to follow another user, identified by the target user's `ID`.",
        summary='Subscribe to a user',
        tags=['Subscriptions']
    ),
)
class UserSubscribeAPIView(SubscriptionMixin):
    serializer_class = sub_s.ChangeUserSubscriptionSerializer
    subscription_model = UserSubscription
    related_model = User
    action = 'subscribe'
    success_message = 'You successfully subscribed'
    object_not_exist_error_msg = 'Such user does not exist'


@extend_schema_view(
    post=extend_schema(
        description="Allows the authenticated user to unfollow another user, identified by the target user's `ID`.",
        summary='Unsubscribe from a user',
        tags=['Subscriptions']
    ),
)
class UserUnsubscribeAPIView(SubscriptionMixin):
    serializer_class = sub_s.ChangeUserSubscriptionSerializer
    subscription_model = UserSubscription
    related_model = User
    action = 'unsubscribe'
    success_message = 'You successfully unsubscribed'
    object_not_exist_error_msg = 'Such user does not exist'


@extend_schema_view(
    post=extend_schema(
        description="Allows the authenticated user to subscribe to a category, identified by the category's `ID`.",
        summary='Subscribe to a category',
        tags=['Subscriptions']
    ),
)
class CategorySubscribeAPIView(SubscriptionMixin):
    serializer_class = sub_s.ChangeCategorySubscriptionSerializer
    subscription_model = CategorySubscription
    related_model = Category
    action = 'subscribe'
    success_message = 'You successfully subscribed'
    object_not_exist_error_msg = 'There is no such category'


@extend_schema_view(
    post=extend_schema(
        description="Allows the authenticated user to unsubscribe from a category, identified by the category's `ID`.",
        summary='Unsubscribe from a category',
        tags=['Subscriptions']
    ),
)
class CategoryUnsubscribeAPIView(SubscriptionMixin):
    serializer_class = sub_s.ChangeCategorySubscriptionSerializer
    subscription_model = CategorySubscription
    related_model = Category
    action = 'unsubscribe'
    success_message = 'You successfully unsubscribed'
    object_not_exist_error_msg = 'There is no such category'


@extend_schema_view(
    get=extend_schema(
        description="Retrieves a list of users that the authenticated user is currently following.",
        summary='Users I am subscribed to',
        tags=['Subscriptions']
    ),
)
class MyUserSubscriptionsAPIView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = UserSubscription.objects.all()
    serializer_class = sub_s.UserSubscriptionListSerializer

    def get_queryset(self):
        queryset = super().get_queryset().select_related('subscribed_to').filter(subscriber=self.request.user)
        return queryset


@extend_schema_view(
    get=extend_schema(
        description="Retrieves a list of categories that the authenticated user is currently subscribed to.",
        summary='Categories I am subscribed to',
        tags=['Subscriptions']
    ),
)
class MyCategoriesSubscriptionsAPIView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = CategorySubscription.objects.all()
    serializer_class = sub_s.CategorySubscriptionListSerializer

    def get_queryset(self):
        queryset = super().get_queryset().select_related('subscribed_to').filter(subscriber=self.request.user)
        return queryset
