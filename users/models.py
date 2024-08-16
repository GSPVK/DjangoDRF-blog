from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django_resized import ResizedImageField
from phonenumber_field.modelfields import PhoneNumberField

from users.managers import CustomUserManager


class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = PhoneNumberField('Phone number', unique=True, blank=True, null=True)

    group_choices = (
        ('Readers', 'Readers'),
        ('Bloggers', 'Bloggers')
    )

    objects = CustomUserManager()

    @property
    def fullname(self) -> str:
        # res = f'{self.first_name}' + ' ' + f'{self.last_name}'
        # return ' '.join(res.split()) if len(res) > 1 else 'No Name'  # 1 is space symbol
        if self.first_name and self.last_name:
            return f'{self.first_name} {self.last_name}'
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return 'No Name'

    @property
    def subscribers_count(self) -> int:
        return self.subscribers.count()

    def get_absolute_url(self):
        return reverse('users:profile', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            Profile.objects.create(user=self)


class Profile(models.Model):
    user = models.OneToOneField('User', on_delete=models.CASCADE, primary_key=True, related_name='profile')
    telegram_id = models.CharField('Telegram', max_length=30, null=True, blank=True)
    photo = ResizedImageField(size=[300, 300],
                              upload_to='profile_photos/',
                              default='default/no-ava.png',
                              force_format='PNG')

    def __str__(self):
        return f'{self.user} (id={self.pk})'

    def get_absolute_url(self):
        return reverse('users:profile', kwargs={'pk': self.pk})
