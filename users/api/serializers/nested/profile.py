from blog.api.serializers import mixins
from common.mixins import serializers as common_s


class MyPostsListSerializer(common_s.TruncateTextSerializer, mixins.PostSerializerMixin):
    ...


class MyCommentsListSerializer(common_s.TruncateTextSerializer, mixins.CommentsSerializerMixin):
    ...
