from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers

from subscription.models import Favorite


@extend_schema_serializer(exclude_fields=['user', 'post', ])
class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = (
            'user',
            'post'
        )
