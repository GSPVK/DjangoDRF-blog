import json

from common.models.ckeditor import CKEditorPostImages
from common.tasks.image import resize_image


class CKEditorPostMiddleware:
    """
    Middleware to record and resize uploaded images from CKEditor.

    This middleware intercepts POST requests to '/ckeditor/upload/' paths.
    It extracts the image URL from the response and saves it to the database
    using the `CKEditorPostImages` model. The image is then resized.

    Note: The images are not directly attached to a blog post. This is handled
    separately using signals.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.method == 'POST' and '/ckeditor/upload/' in request.path:
            try:
                db_images = CKEditorPostImages()
                db_images.uri = json.loads(response.content)['url']
                db_images.save()
                resize_image.delay_on_commit(db_images.uri)
            except KeyError:
                pass
        return response
