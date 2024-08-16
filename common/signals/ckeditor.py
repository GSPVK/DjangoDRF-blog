from django.db import transaction
from django.db.models.signals import pre_save, post_save, pre_delete
from django.dispatch import receiver
from django.db.models import Q
from common.models.ckeditor import CKEditorPostImages
from blog.models import Post
from common.tasks.image import delete_image
import re


# Two save's signals are not combined into one because the instance.pk check ensures that we do not work with a post
# that is being created for the first time. post_save will always have instance.pk. This helps to offload the logic.


@receiver(pre_save, sender=Post, dispatch_uid='common.post.pre_save_posts')
def pre_save_posts(sender, instance, **kwargs):
    """
    Signal handler to manage images before saving a post.

    If the post is being updated, removes associations with images no longer
    present in the post's text.
    """
    if instance.pk:
        images = re.findall('<img.*src=\"([^\"]+)', instance.text)
        excluded_images = CKEditorPostImages.objects.filter(Q(posts=instance) & ~Q(uri__in=images))
        if excluded_images.exists():
            for image in excluded_images:
                image.posts.remove(instance)


@receiver(post_save, sender=Post, dispatch_uid='common.post.post_save_posts')
def post_save_posts(sender, instance, **kwargs):
    """
    Signal handler to manage images after saving a post.

    Finds all images in the post's text, associates existing images with the post,
    then deletes any orphaned images.
    """
    images = re.findall('<img.*src=\"([^\"]+)', instance.text)
    db_images = CKEditorPostImages.objects.filter(~Q(posts=instance) & Q(uri__in=images))

    with transaction.atomic():
        for row in db_images:
            row.posts.add(instance)

        orphan_images = CKEditorPostImages.objects.filter(posts__isnull=True)
        for image in orphan_images:
            delete_image.delay_on_commit(image.uri)

        orphan_images.delete()


@receiver(pre_delete, sender=Post, dispatch_uid='common.post.post_delete_blog')
def pre_delete_post(sender, instance, **kwargs):
    """
    Find all images associated with the post being deleted.
    Detach them from the post and delete them if they are no longer associated with any posts.
    """
    db_images = CKEditorPostImages.objects.filter(posts=instance)

    with transaction.atomic():
        for row in db_images:
            row.posts.remove(instance)
            if not row.posts.exists():
                row.delete()
                delete_image.delay_on_commit(row.uri)
