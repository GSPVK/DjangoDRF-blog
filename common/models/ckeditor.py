from django.db import models
from blog.models import Post


class CKEditorPostImages(models.Model):
    uri = models.CharField(max_length=250)
    posts = models.ManyToManyField(Post)
