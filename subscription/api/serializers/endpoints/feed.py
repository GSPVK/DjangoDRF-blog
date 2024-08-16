from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers

from subscription.models import UserSubscription


class ChangeUserSubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserSubscription
        fields = ('subscriber', 'subscribed_to')