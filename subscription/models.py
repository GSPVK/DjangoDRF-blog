from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    post = models.ForeignKey('blog.Post', on_delete=models.CASCADE, related_name='favorites')

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=['user', 'post'],
                name='unique_favorite'
            ),
        )


class CategorySubscription(models.Model):
    subscriber = models.ForeignKey(User, on_delete=models.CASCADE, related_name='category_subscriptions')
    subscribed_to = models.ForeignKey('blog.Category', on_delete=models.CASCADE, related_name='subscribers')

    class Meta:
        ordering = ('subscribed_to',)
        constraints = (
            models.UniqueConstraint(
                fields=['subscriber', 'subscribed_to'],
                name='unique_category_subscription'
            ),
        )

    def __str__(self):
        return f'{self.subscriber} subscribed to category: {self.subscribed_to}'


class UserSubscription(models.Model):
    subscriber = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_subscriptions')
    subscribed_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscribers')

    class Meta:
        ordering = ('subscribed_to',)
        constraints = (
            models.UniqueConstraint(
                fields=['subscriber', 'subscribed_to'],
                name='unique_user_subscription'
            ),
        )

    def __str__(self):
        return f'{self.subscriber} subscribed to user: {self.subscribed_to}'
