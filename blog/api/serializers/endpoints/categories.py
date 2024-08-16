from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from blog.api.serializers import mixins as cat_mixin
from subscription.models import CategorySubscription


class CategorySerializer(cat_mixin.CategorySerializerMixin):
    ...


class CategoryRetrieveSerializer(cat_mixin.CategorySerializerMixin):
    posts_count = serializers.IntegerField(source='posts.count')
    subscribers = serializers.IntegerField(source='subscribers.count')
    subscribed = serializers.SerializerMethodField()

    class Meta(cat_mixin.CategorySerializerMixin.Meta):
        fields = cat_mixin.CategorySerializerMixin.Meta.fields + ('posts_count', 'subscribers', 'subscribed')

    @extend_schema_field(serializers.BooleanField)
    def get_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated and CategorySubscription.objects.filter(
                subscriber=request.user,
                subscribed_to=obj
        ).exists():
            return True
        return False
