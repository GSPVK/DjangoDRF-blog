from rest_framework.permissions import IsAuthenticated, BasePermission, SAFE_METHODS


class IsPostAuthorPermission(IsAuthenticated):
    message = 'You are not author of this post'

    def has_object_permission(self, request, view, obj):
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            return request.user == obj.author.user or request.user.is_staff
        return True


class IsBloggerPermission(BasePermission):
    message = 'You are not in the Bloggers group to create posts'

    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user and request.user.groups.filter(name='Bloggers').exists()
        return True


class IsCommentAuthorPermission(IsAuthenticated):
    message = 'You are not author of this comment'

    def has_object_permission(self, request, view, obj):
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            return request.user == obj.author or request.user.is_staff
        return True


class IsAdminOrReadOnly(IsAuthenticated):
    message = 'You are not admin'

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return request.user.is_staff
