from drf_spectacular.utils import extend_schema_serializer, extend_schema_field
from rest_framework import serializers
from rest_framework.reverse import reverse_lazy

from subscription.models import UserSubscription, CategorySubscription


@extend_schema_serializer(exclude_fields=['subscriber', 'subscribed_to'])
class ChangeUserSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSubscription
        fields = ('subscriber', 'subscribed_to')


@extend_schema_serializer(exclude_fields=['subscriber', 'subscribed_to'])
class ChangeCategorySubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategorySubscription
        fields = ('subscriber', 'subscribed_to')


class UserSubscriptionListSerializer(serializers.HyperlinkedModelSerializer):
    user_id = serializers.ReadOnlyField(source='subscribed_to.id')
    username = serializers.StringRelatedField(source='subscribed_to')
    user_profile = serializers.HyperlinkedRelatedField(source='subscribed_to', view_name='users:profile', read_only=True)

    class Meta:
        model = UserSubscription
        fields = ('user_id', 'username', 'user_profile',)


class CategorySubscriptionListSerializer(serializers.ModelSerializer):
    category_id = serializers.ReadOnlyField(source='subscribed_to.id')
    category_title = serializers.StringRelatedField(source='subscribed_to')
    category_page = serializers.SerializerMethodField()

    @extend_schema_field(serializers.URLField)
    def get_category_page(self, obj):
        title = obj.subscribed_to.title
        request = self.context.get('request')
        return request.build_absolute_uri(reverse_lazy('blog:posts') + f'?category={title}')

    class Meta:
        model = UserSubscription
        fields = ('category_id', 'category_title', 'category_page')
