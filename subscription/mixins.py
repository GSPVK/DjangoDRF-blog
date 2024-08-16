from typing import Optional

from django.core.exceptions import ImproperlyConfigured
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class SubscriptionMixin(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    subscription_model = None
    related_model = None
    action: str = None
    success_message: Optional[str] = None
    default_error_msg: str = 'Something went wrong'
    already_subscribed_error_msg: str = 'You already subscribed'
    subscription_not_exist_error_msg: str = 'Subscription does not exist'
    object_not_exist_error_msg: Optional[str] = None

    def post(self, request, *args, **kwargs):
        self.validate_configuration()

        data = {
            'subscriber': self.request.user.pk,
            'subscribed_to': self.kwargs.get('pk')
        }

        if self.action == 'subscribe':
            return self.handle_subscribe(data)

        elif self.action == 'unsubscribe':
            return self.handle_unsubscribe(data)

        raise ValidationError(f"Invalid action: {self.action}")

    def validate_configuration(self):
        missing_attrs = {
            'subscription_model': '"%s" should include attribute `subscription_model`',
            'related_model': '"%s" should include attribute `related_model`',
            'action': '"%s" should include attribute `action`',
        }

        for attr, error_msg in missing_attrs.items():
            if not getattr(self, attr):
                raise ImproperlyConfigured(error_msg % self.__class__.__name__)

    def handle_subscribe(self, data):
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(data={'success': self.success_message}, status=status.HTTP_201_CREATED)
        else:
            errors = serializer.errors

            if 'non_field_errors' in errors and any(error.code == 'unique' for error in errors['non_field_errors']):
                return Response(data={'error': f'{self.already_subscribed_error_msg}'}, status=status.HTTP_409_CONFLICT)

            if 'subscribed_to' in errors and any(error.code == 'does_not_exist' for error in errors['subscribed_to']):
                return Response(data={'error': f'{self.object_not_exist_error_msg}'}, status=status.HTTP_404_NOT_FOUND)

            return Response(data={'error': f'{self.default_error_msg}'}, status=status.HTTP_400_BAD_REQUEST)

    def handle_unsubscribe(self, data):
        existing_subscription = self.subscription_model.objects.filter(
            subscriber_id=data['subscriber'], subscribed_to=data['subscribed_to']
        ).first()

        if existing_subscription:
            existing_subscription.delete()
            return Response(data={'success': f'{self.success_message}'}, status=status.HTTP_204_NO_CONTENT)
        elif not self.related_model.objects.filter(pk=data['subscribed_to']).exists():
            return Response(data={'error': f'{self.object_not_exist_error_msg}'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(data={'error': f'{self.subscription_not_exist_error_msg}'}, status=status.HTTP_404_NOT_FOUND)
