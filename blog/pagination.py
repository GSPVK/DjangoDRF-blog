from rest_framework.pagination import CursorPagination


class CursorCreatedAtPagination(CursorPagination):
    ordering = '-created_at'


def paginate_and_serialize_objects(objects, paginator, serializer, request):
    """
    Paginate and serialize posts or comments.
    """
    paginated = paginator.paginate_queryset(objects, request)
    serialized = serializer(paginated, many=True, context={'request': request}).data

    result = {
        'results': serialized,
        'count': paginator.page.paginator.count,
    }

    if paginator.get_next_link():
        result['next'] = paginator.get_next_link()
    if paginator.get_previous_link():
        result['previous'] = paginator.get_previous_link()

    return result
