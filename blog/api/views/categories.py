from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, viewsets

from blog.api.serializers.endpoints import categories as categories_s
from blog.models import Category
from blog.permissions import IsAdminOrReadOnly
from common.mixins.views import ExtendedView


@extend_schema_view(
    list=extend_schema(
        description='Returns a list of categories.',
        summary='Get a list of categories',
        tags=['Category'],
    ),
    retrieve=extend_schema(
        description='Returns a detailed information about a category.',
        summary='Retrieve information about a category.',
        tags=['Category'],
    ),
    create=extend_schema(
        description="The create action expects the `name` field, creates a new category, and returns it.",
        summary='Create a new category',
        tags=['Category']
    ),
    partial_update=extend_schema(
        description="The partial update action modifies specific fields of a category identified by `id`.",
        summary='Update category name (partial)',
        tags=['Category']
    ),
    update=extend_schema(
        description="The full update action replaces the entire category identified by `id`.",
        summary='Update category name (full)',
        tags=['Category']
    ),
    destroy=extend_schema(
        description="The destroy action deletes a single category identified by `id`.",
        summary='Delete a category',
        tags=['Category']
    )
)
class CategoryViewSet(ExtendedView, viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = categories_s.CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ('id', 'title',)
    ordering = ('id',)

    multi_serializer_class = {
        'retrieve': categories_s.CategoryRetrieveSerializer,
    }

    def get_object(self):
        if self.action == 'retrieve':
            return self.queryset.prefetch_related('posts', 'subscribers').get(id=self.kwargs['pk'])
        return super().get_object()
