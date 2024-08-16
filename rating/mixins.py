from typing import Optional

from django.core.exceptions import ImproperlyConfigured
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from rating.models import Vote


class VoteAPIMixin(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    rating_model = None
    vote: Optional[Vote.VoteType] = None
    success_message: Optional[str] = None
    vote_removed_message: Optional[str] = None

    def post(self, request, *args, **kwargs):
        self.validate_configuration()

        data = {
            'obj': self.kwargs.get('pk'),
            'owner': request.user.pk,
            'vote': self.vote
        }

        vote_obj = self.rating_model.objects.filter(
            obj=self.kwargs.get('pk'),
            owner=request.user.pk
        ).first()

        if not vote_obj:
            resp = {'data': {'success': self.success_message}, 'status': status.HTTP_201_CREATED}
        elif vote_obj.vote != self.vote:
            resp = {'data': {'success': self.success_message}, 'status': status.HTTP_200_OK}
        else:
            # If the existing vote is equal to the vote entered by the user - make it neutral.
            data['vote'] = Vote.VoteType.NEUTRAL
            resp = {'data': {'success': self.vote_removed_message}, 'status': status.HTTP_200_OK}

        serializer = self.serializer_class(instance=vote_obj or None, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(**resp)

    def validate_configuration(self):
        missing_attrs = {
            'rating_model': '"%s" should include attribute `rating_model`',
            'vote': '"%s" should include attribute `vote`',
        }

        for attr, error_msg in missing_attrs.items():
            if not getattr(self, attr):
                raise ImproperlyConfigured(error_msg % self.__class__.__name__)
