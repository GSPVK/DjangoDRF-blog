from rest_framework.renderers import BrowsableAPIRenderer


class OnlyRawBrowsableAPIRenderer(BrowsableAPIRenderer):
    def render_form_for_serializer(self, serializer):
        return ""
