from django.test import TestCase, RequestFactory, Client
from django.http import HttpResponse
from unittest.mock import patch, MagicMock
import json

from common.middlewares.ckeditor import CKEditorPostMiddleware
from common.models.ckeditor import CKEditorPostImages


class CKEditorPostMiddlewareTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = CKEditorPostMiddleware(get_response=MagicMock(return_value=HttpResponse()))

    @patch('common.middlewares.ckeditor.resize_image.delay_on_commit')
    def test_ckeditor_upload_post(self, mock_resize_image):
        request = self.factory.post('/ckeditor/upload/')
        mock_response = HttpResponse(json.dumps({'url': '/media/test_image.jpg'}), content_type='application/json')
        self.middleware.get_response.return_value = mock_response
        self.middleware(request)
        self.assertEqual(CKEditorPostImages.objects.count(), 1)
        saved_image = CKEditorPostImages.objects.first()
        self.assertEqual(saved_image.uri, '/media/test_image.jpg')
        mock_resize_image.assert_called_once_with('/media/test_image.jpg')

    @patch('common.middlewares.ckeditor.resize_image.delay_on_commit')
    def test_non_ckeditor_request(self, mock_resize_image):
        request = self.factory.get('/some-other-url/')
        self.middleware(request)
        self.assertEqual(CKEditorPostImages.objects.count(), 0)
        mock_resize_image.assert_not_called()

    @patch('common.middlewares.ckeditor.resize_image.delay_on_commit')
    def test_ckeditor_upload_post_no_url(self, mock_resize_image):
        request = self.factory.post('/ckeditor/upload/')
        mock_response = HttpResponse(json.dumps({}), content_type='application/json')
        self.middleware.get_response.return_value = mock_response
        self.middleware(request)
        self.assertEqual(CKEditorPostImages.objects.count(), 0)
        mock_resize_image.assert_not_called()
