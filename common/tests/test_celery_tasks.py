from pathlib import Path
from unittest.mock import patch
from django.test import TestCase
from django.conf import settings
from PIL import Image

from common.tasks.image import delete_image, resize_image


class CeleryTasksTestCase(TestCase):
    def setUp(self):
        self.test_dir = Path(settings.BASE_DIR) / 'test_images'
        self.test_dir.mkdir(exist_ok=True)

    def tearDown(self):
        for file in self.test_dir.iterdir():
            file.unlink()
        self.test_dir.rmdir()

    @patch('common.tasks.image.Path')
    def test_delete_image(self, mock_path):
        test_image_path = '/test_images/test.jpg'

        delete_image(test_image_path)

        mock_path.assert_any_call(str(settings.BASE_DIR) + test_image_path)
        mock_path.assert_any_call(str(settings.BASE_DIR) + '/test_images/test_thumb.jpg')
        self.assertEqual(mock_path().unlink.call_count, 2)

    def test_resize_image_large(self):
        test_image_path = self.test_dir / 'test_large.jpg'
        img = Image.new('RGB', (2000, 1500), color='red')
        img.save(test_image_path)

        resize_image('/test_images/test_large.jpg')

        resized_img = Image.open(test_image_path)
        self.assertLessEqual(resized_img.width, 1920)
        self.assertLessEqual(resized_img.height, 1080)

    def test_resize_image_small(self):
        test_image_path = self.test_dir / 'test_small.jpg'
        img = Image.new('RGB', (800, 600), color='blue')
        img.save(test_image_path)

        resize_image('/test_images/test_small.jpg')

        resized_img = Image.open(test_image_path)
        self.assertEqual(resized_img.width, 800)
        self.assertEqual(resized_img.height, 600)
