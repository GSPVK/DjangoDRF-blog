import re

from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

from common.models.mixins import DateTimeMixin
from rating.models import PostRating, Vote, CommentRating
from .managers import PostManager, CommentManager

User = get_user_model()


class Author(models.Model):
    class Meta:
        ordering = ('user__username',)

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField('Biography', max_length=1000, blank=True, default='Empty')

    def __str__(self):
        return self.user.username  # noqa


class Post(DateTimeMixin):
    class Meta:
        ordering = ('-created_at',)

    author = models.ForeignKey('Author', on_delete=models.CASCADE, related_name='posts')
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=100)
    text = RichTextUploadingField(max_length=3000, help_text='Enter text')

    objects = PostManager()

    @property
    def comments_count(self):
        return self.comments.count()

    @property
    def fav_count(self):
        return self.favorites.count()

    def get_absolute_url(self):
        return reverse('blog:post-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            PostRating.objects.create(obj=self, owner=self.author.user, vote=Vote.VoteType.NEUTRAL)


class Category(models.Model):
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ('title',)

    title = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.title


class Comment(DateTimeMixin):
    class Meta:
        ordering = ('-created_at',)

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='comments')
    reply_to = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    text = RichTextField(config_name='comments', max_length=600,
                         help_text='Comment length should not exceed 400 characters')

    objects = CommentManager()

    def __str__(self):
        clean_text = re.sub(r'<[^>]+>', '', self.text)[:15]
        return clean_text

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            CommentRating.objects.create(obj=self, owner=self.author, vote=Vote.VoteType.NEUTRAL)
