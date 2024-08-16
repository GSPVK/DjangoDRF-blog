from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):
    help = "Sets up default groups 'Bloggers' and 'Readers' and assigns permissions to 'Bloggers'."

    def handle(self, *args, **options):
        readers, r_created = Group.objects.get_or_create(name='Readers')
        bloggers, b_created = Group.objects.get_or_create(name='Bloggers')

        add_blog_perm = Permission.objects.get(codename='add_post', content_type__app_label='blog')
        bloggers.permissions.add(add_blog_perm)

        try:
            content_type = ContentType.objects.get(app_label='blog', model='post')
            add_blog_perm = Permission.objects.get(codename='add_post', content_type=content_type)

            bloggers.permissions.add(add_blog_perm)
            self.stdout.write(self.style.SUCCESS("Successfully assigned 'add_post' permission to 'Bloggers' group."))

        except ContentType.DoesNotExist:
            raise CommandError("ContentType 'blog.post' does not exist. Make sure the 'blog' app is migrated.")

        except Permission.DoesNotExist:
            raise CommandError("Permission 'add_post' does not exist. Ensure the 'blog' app has correct permissions.")

        if r_created:
            self.stdout.write(self.style.SUCCESS("Successfully created 'Readers' group."))
        else:
            self.stdout.write(self.style.NOTICE("'Readers' group already exists."))

        if b_created:
            self.stdout.write(self.style.SUCCESS("Successfully created 'Bloggers' group."))
        else:
            self.stdout.write(self.style.NOTICE("'Bloggers' group already exists."))
