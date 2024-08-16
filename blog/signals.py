from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.cache import cache
from django.db.models.signals import m2m_changed, post_save, post_delete
from django.dispatch import receiver

from blog import constants as const
from blog.models import Author, Category

User = get_user_model()


@receiver([post_save, post_delete], sender=Category, dispatch_uid='blog.update_category_cache')
def update_category_cache(sender, **kwargs):
    """
    Updates the category cache when data in the Category model changes.
    """
    cached_choices = [
        (category.title, category.title) for category in Category.objects.all()
    ]
    cache.set(const.CATEGORY_CACHE_KEY, cached_choices)


@receiver(m2m_changed, sender=User.groups.through, dispatch_uid='blog.create_or_delete_blog_author')
def create_or_delete_blog_author(sender, instance, action, **kwargs):
    """
    Signal handler to create or delete an Author instance upon changes to a User's group memberships.

    This signal is triggered when a User's group membership changes. If the User is added to the 'Bloggers' group,
    an Author instance is created for that User.
    Conversely, if the User is removed from the 'Bloggers' group, their Author instance is deleted.

    """
    if action == 'post_add' and instance.groups.filter(name='Bloggers').exists():
        Author.objects.get_or_create(user=instance)

    elif action == 'post_remove' and not instance.groups.filter(name='Bloggers').exists():
        try:
            author = Author.objects.get(user=instance)
            author.delete()
        except Author.DoesNotExist:
            pass


@receiver(post_save, sender=User, dispatch_uid='blog.ensure_superusers_blogger_group_membership')
def ensure_superusers_have_blogger_group_membership(sender, instance, created, **kwargs):
    """
    Automatically adding new superusers to the 'Bloggers' group and creating an associated
    'Author' profile.
    """
    if created and instance.is_superuser:
        group, _ = Group.objects.get_or_create(name='Bloggers')
        if not instance.groups.filter(name='Bloggers').exists():
            instance.groups.add(group)

        Author.objects.get_or_create(user=instance)
