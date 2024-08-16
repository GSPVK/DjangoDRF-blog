from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from blog.models import Post, Category, Author
from subscription.models import Favorite, CategorySubscription, UserSubscription

User = get_user_model()


class FavoritesViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='1X<ISRUkw+tuK', email='em@il.com')
        cls.category = Category.objects.create(title='BlogCategory')
        cls.author = Author.objects.create(user=cls.user, bio='Biography')
        cls.post1 = Post.objects.create(author=cls.author, category=cls.category, title='Post 1', text='Content 1')
        cls.post2 = Post.objects.create(author=cls.author, category=cls.category, title='Post 2', text='Content 2')
        Favorite.objects.create(user=cls.user, post=cls.post1)

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.user)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('subscription:my-favorites'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('subscription:my-favorites'))
        self.assertTemplateUsed(response, 'subscription/favorites.html')

    def test_favorites_pagination_is_10(self):
        for i in range(11):
            post = Post.objects.create(author=self.author, category=self.category, title=f'Post {i + 3}',
                                       text=f'Content {i + 3}')
            Favorite.objects.create(user=self.user, post=post)

        response = self.client.get(reverse('subscription:my-favorites'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['is_paginated'])
        self.assertEqual(len(response.context['object_list']), 10)

    def test_favorites_view_queryset(self):
        response = self.client.get(reverse('subscription:my-favorites'))
        self.assertQuerySetEqual(response.context['object_list'], [self.post1], ordered=False)


class ChangeFavoriteViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='1X<ISRUkw+tuK', email='em@il.com')
        cls.category = Category.objects.create(title='BlogCategory')
        cls.author = Author.objects.create(user=cls.user, bio='Biography')
        cls.post1 = Post.objects.create(author=cls.author, category=cls.category, title='Post 1', text='Content 1')
        cls.post2 = Post.objects.create(author=cls.author, category=cls.category, title='Post 2', text='Content 2')

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.user)

    def test_add_favorite(self):
        response = self.client.post(reverse('subscription:change-favorite', args=[self.post1.pk, 'add']))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Favorite.objects.filter(user=self.user, post=self.post1).exists())

    def test_remove_favorite(self):
        Favorite.objects.create(user=self.user, post=self.post1)
        response = self.client.post(reverse('subscription:change-favorite', args=[self.post1.pk, 'remove']))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Favorite.objects.filter(user=self.user, post=self.post1).exists())

    def test_invalid_action(self):
        response = self.client.post(reverse('subscription:change-favorite', args=[self.post1.pk, 'invalid']))
        self.assertEqual(response.status_code, 400)

    def test_object_to_favorite_does_not_exist(self):
        response = self.client.post(reverse('subscription:change-favorite', args=[999999, 'add']))
        self.assertEqual(response.status_code, 404)


class FeedListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='1X<ISRUkw+tuK', email='em@il.com')
        cls.category = Category.objects.create(title='BlogCategory')
        cls.author = Author.objects.create(user=cls.user, bio='Biography')
        cls.post1 = Post.objects.create(author=cls.author, category=cls.category, title='Post 1', text='Content 1')
        cls.post2 = Post.objects.create(author=cls.author, category=cls.category, title='Post 2', text='Content 2')
        CategorySubscription.objects.create(subscriber=cls.user, subscribed_to=cls.category)

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.user)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('subscription:my-feed'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('subscription:my-feed'))
        self.assertTemplateUsed(response, 'subscription/feed.html')

    def test_feed_view_pagination(self):
        for i in range(15):
            Post.objects.create(author=self.author, category=self.category, title=f'Post {i + 3}',
                                text=f'Content {i + 3}')

        response = self.client.get(reverse('subscription:my-feed'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['object_list']), 10)

    def test_feed_view_queryset(self):
        response = self.client.get(reverse('subscription:my-feed'))
        self.assertQuerySetEqual(response.context['object_list'], [self.post1, self.post2], ordered=False)


class ChangeSubscriptionViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='1X<ISRUkw+tuK', email='em@il.com')
        cls.category = Category.objects.create(title='Test Category')
        cls.another_user = User.objects.create_user(username='anotheruser', password='1X<ISRUkw+tuK', email='em@ial.com')

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.user)

    def test_subscribe_to_category(self):
        response = self.client.post(reverse('subscription:change-subscription', args=['category', self.category.pk, 'subscribe']))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(CategorySubscription.objects.filter(subscriber=self.user, subscribed_to=self.category).exists())

    def test_unsubscribe_from_category(self):
        CategorySubscription.objects.create(subscriber=self.user, subscribed_to=self.category)
        response = self.client.post(reverse('subscription:change-subscription', args=['category', self.category.pk, 'unsubscribe']))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            CategorySubscription.objects.filter(subscriber=self.user, subscribed_to=self.category).exists())

    def test_subscribe_to_user(self):
        response = self.client.post(reverse('subscription:change-subscription', args=['user', self.another_user.pk, 'subscribe']))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(UserSubscription.objects.filter(subscriber=self.user, subscribed_to=self.another_user).exists())

    def test_unsubscribe_from_user(self):
        UserSubscription.objects.create(subscriber=self.user, subscribed_to=self.another_user)
        response = self.client.post(reverse('subscription:change-subscription', args=['user', self.another_user.pk, 'unsubscribe']))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            UserSubscription.objects.filter(subscriber=self.user, subscribed_to=self.another_user).exists())

    def test_object_to_subscribe_does_not_exist(self):
        response = self.client.post(reverse('subscription:change-subscription', args=['category', 999999, 'subscribe']))
        self.assertEqual(response.status_code, 404)

    def test_invalid_object_type(self):
        response = self.client.post(reverse('subscription:change-subscription', args=['invalid', self.category.pk, 'subscribe']))
        self.assertEqual(response.status_code, 404)

    def test_invalid_action(self):
        response = self.client.post(reverse('subscription:change-subscription', args=['category', self.category.pk, 'invalid']))
        self.assertEqual(response.status_code, 200)


class MySubscriptionsListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='1X<ISRUkw+tuK', email='em@il.com')
        cls.category = Category.objects.create(title='BlogCategory')
        cls.user_to_subscribe = User.objects.create_user(username='testuser2', password='1X<ISRUkw+tuK',
                                                         email='em@ial.com')

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.user)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('subscription:my-subscriptions'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('subscription:my-subscriptions'))
        self.assertTemplateUsed(response, 'subscription/subscriptions.html')

    def test_my_user_subscriptions_pagination_is_10(self):
        for i in range(11):
            user_to_subscribe = User.objects.create_user(username=f'testuser{i + 3}', password='1X<ISRUkw+tuK',
                                                         email=f'em@i{i + 3}al.com')
            UserSubscription.objects.create(subscriber=self.user, subscribed_to=user_to_subscribe)

        response = self.client.get(reverse('subscription:my-subscriptions'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['followed_users']), 10)

    def test_my_category_subscriptions_pagination_is_10(self):
        for i in range(11):
            category = Category.objects.create(title=f'Category {i + 1}')
            CategorySubscription.objects.create(subscriber=self.user, subscribed_to=category)

        response = self.client.get(reverse('subscription:my-subscriptions'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['followed_categories']), 10)
