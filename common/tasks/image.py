from pathlib import Path

from PIL import Image
from celery import shared_task

from config.settings import BASE_DIR


@shared_task
def delete_image(image_path: str):
    """
    This function assumes that the file extension of the images is '.jpg'. This is
    based on the `CKEDITOR_FORCE_JPEG_COMPRESSION = True` setting, which forces the
    use of JPEG compression for images.
    """
    Path(str(BASE_DIR) + image_path).unlink(missing_ok=True)

    # line below excluding the last four characters, which are assumed to be the file extension '.jpg',
    # appending '_thumb.jpg', and then deleting the file at that path
    Path(str(BASE_DIR) + image_path[:-4] + '_thumb.jpg').unlink(missing_ok=True)


@shared_task
def resize_image(image_path: str):
    img_path = str(BASE_DIR) + image_path
    img = Image.open(img_path)
    width, height = img.size

    if width > 1920 or height > 1080:
        img.thumbnail((1920, 1080))
        img.save(img_path)
