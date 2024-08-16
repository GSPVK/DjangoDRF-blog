from django.contrib import admin
from django.core.exceptions import ValidationError


class ExtendedModelAdmin(admin.ModelAdmin):

    def get_object_queryset(self, request):
        """
        Get the queryset used for retrieving a single object to be edited.

        By default, this method uses the same `get_queryset` method as the view itself.
        To change this behavior, override this method with a custom queryset that
        excludes unnecessary prefetches or selects required only for the list view
        to optimize the performance of the edit page.
        """
        return self.get_queryset(request)

    def get_object(self, request, object_id, from_field=None):
        """
        This method overrides the standard `get_object` method to use a custom
        queryset defined in `get_object_queryset`.
        Aside from using a different queryset, this method is otherwise identical
        to the default `get_object`.
        """
        queryset = self.get_object_queryset(request)
        model = queryset.model
        field = (
            model._meta.pk if from_field is None else model._meta.get_field(from_field)
        )
        try:
            object_id = field.to_python(object_id)
            return queryset.get(**{field.name: object_id})
        except (model.DoesNotExist, ValidationError, ValueError):
            return None
