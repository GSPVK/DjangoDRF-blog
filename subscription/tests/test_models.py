from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

from blog.models import Post, Category, Author
from subscription.models import Favorite, CategorySubscription, UserSubscription

User = get_user_model()


class FavoriteModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.post_author_user = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK', email='em@il.com')
        cls.author = Author.objects.create(user=cls.post_author_user, bio='Biography')
        cls.category = Category.objects.create(title='BlogCategory')
        cls.post = Post.objects.create(author=cls.author, category=cls.category, title='Post 1', text='Content 1')
        cls.favorite = Favorite.objects.create(user=cls.post_author_user, post=cls.post)

    def test_user_label(self):
        field_label = self.favorite._meta.get_field('user').verbose_name
        self.assertEqual(field_label, 'user')

    def test_post_label(self):
        field_label = self.favorite._meta.get_field('post').verbose_name
        self.assertEqual(field_label, 'post')

    def test_unique_constraint(self):
        with self.assertRaises(IntegrityError):
            Favorite.objects.create(user=self.post_author_user, post=self.post)


class CategorySubscriptionModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK', email='em@il.com')
        cls.category = Category.objects.create(title='BlogCategory')
        cls.subscription = CategorySubscription.objects.create(subscriber=cls.user, subscribed_to=cls.category)

    def test_subscriber_label(self):
        field_label = self.subscription._meta.get_field('subscriber').verbose_name
        self.assertEqual(field_label, 'subscriber')

    def test_subscribed_to_label(self):
        field_label = self.subscription._meta.get_field('subscribed_to').verbose_name
        self.assertEqual(field_label, 'subscribed to')

    def test_unique_constraint(self):
        with self.assertRaises(IntegrityError):
            CategorySubscription.objects.create(subscriber=self.user, subscribed_to=self.category)

    def test_str_method(self):
        self.assertEqual(str(self.subscription), f'{self.user} subscribed to category: {self.category}')


class UserSubscriptionModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK', email='em@il.com')
        cls.user2 = User.objects.create_user(username='testuser2', password='1X<ISRUkw+tuK', email='em@ail.com')
        cls.subscription = UserSubscription.objects.create(subscriber=cls.user1, subscribed_to=cls.user2)

    def test_subscriber_label(self):
        field_label = self.subscription._meta.get_field('subscriber').verbose_name
        self.assertEqual(field_label, 'subscriber')

    def test_subscribed_to_label(self):
        field_label = self.subscription._meta.get_field('subscribed_to').verbose_name
        self.assertEqual(field_label, 'subscribed to')

    def test_unique_constraint(self):
        with self.assertRaises(IntegrityError):
            UserSubscription.objects.create(subscriber=self.user1, subscribed_to=self.user2)

    def test_str_method(self):
        self.assertEqual(str(self.subscription), f'{self.user1} subscribed to user: {self.user2}')
