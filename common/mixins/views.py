from collections import defaultdict

from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, UpdateModelMixin, ListModelMixin
from rest_framework.viewsets import GenericViewSet


class ExtendedView:
    multi_permission_classes = None
    multi_serializer_class = None
    request = None

    def get_serializer_class(self):
        assert self.serializer_class or self.multi_serializer_class, (
                '"%s" should either include `serializer_class`, '
                '`multi_serializer_class`, attribute, or override the '
                '`get_serializer_class()` method.' % self.__class__.__name__
        )
        if not self.multi_serializer_class:
            return self.serializer_class

        # define request action or method
        if getattr(self, 'action', None):
            action = self.action
        else:
            action = self.request.method

        # Trying to get action serializer or default
        return self.multi_serializer_class.get(action) or self.serializer_class


class CUDLViewSet(GenericViewSet, CreateModelMixin, UpdateModelMixin, DestroyModelMixin, ListModelMixin):
    ...


class CommentTreeMixin:
    """
    This mixin provides functionality to structure comments into a tree format,
    where each comment can have nested replies. It also handles the pagination
    of root comments and limits the number of visible replies for each comment.
    """
    root_comments_paginate_by = 5
    comment_replies_limit = 3

    def comment_tree(self, comments):
        """
        Organize a list of comments into a tree structure with limited replies.

        This method organizes comments into a tree structure where each comment
        may have nested replies. Each comment's replies are stored in a list and
        the number of visible replies is limited according to the
        `comment_replies_limit` attribute. Any additional replies beyond this limit
        are stored separately.
        """

        parent_comments = defaultdict(list)

        # Populate the dictionary with comments, grouping them by their parent ID
        for comment in comments:
            parent_comments[comment.reply_to_id].append(comment)

        # Iterate over comments to assign their replies and handle reply limits
        for comment in comments:
            comment.replies_list = parent_comments[comment.pk]
            comment.replies_count = len(comment.replies_list)

            comment.replies_more = comment.replies_list[self.comment_replies_limit:]
            comment.replies_list = comment.replies_list[:self.comment_replies_limit]

        # Return the list of root comments (comments with no parent)
        root_comments = parent_comments[None]
        return root_comments
