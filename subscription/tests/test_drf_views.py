from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from blog.models import Post, Author, Category
from subscription.models import Favorite, CategorySubscription, UserSubscription

User = get_user_model()


class AddFavoriteAPIViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.post_author_user = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK',
                                                        email='em@il.com')
        cls.author = Author.objects.create(user=cls.post_author_user, bio='Biography')
        cls.category = Category.objects.create(title='BlogCategory')
        cls.post = Post.objects.create(author=cls.author, category=cls.category, title='Post 1', text='Content 1')

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.post_author_user)

    def test_add_favorite(self):
        url = reverse('api:add-favorite', kwargs={'pk': self.post.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['success'], 'Post added to favorites!')
        favorite = Favorite.objects.get(user=self.post_author_user, post=self.post)
        self.assertIsNotNone(favorite)

    def test_already_favorited(self):
        Favorite.objects.create(user=self.post_author_user, post=self.post)
        url = reverse('api:add-favorite', kwargs={'pk': self.post.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['success'], 'Post already in favorites.')

    def test_post_not_exists(self):
        url = reverse('api:add-favorite', kwargs={'pk': 9999})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_not_authenticated(self):
        self.client = APIClient()
        url = reverse('api:add-favorite', kwargs={'pk': self.post.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class RemoveFavoriteAPIViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.post_author_user = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK',
                                                        email='em@il.com')
        cls.author = Author.objects.create(user=cls.post_author_user, bio='Biography')
        cls.category = Category.objects.create(title='BlogCategory')
        cls.post = Post.objects.create(author=cls.author, category=cls.category, title='Post 1', text='Content 1')

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.post_author_user)

    def test_remove_favorite(self):
        Favorite.objects.create(user=self.post_author_user, post=self.post)
        url = reverse('api:remove-favorite', kwargs={'pk': self.post.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], 'Post removed from favorites!')
        self.assertFalse(Favorite.objects.filter(user=self.post_author_user, post=self.post).exists())

    def test_favorite_not_found(self):
        url = reverse('api:remove-favorite', kwargs={'pk': self.post.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_not_authenticated(self):
        self.client = APIClient()
        url = reverse('api:remove-favorite', kwargs={'pk': self.post.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class MyFavoritesAPIViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.post_author_user = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK',
                                                        email='em@il.com')
        cls.author = Author.objects.create(user=cls.post_author_user, bio='Biography')
        cls.category = Category.objects.create(title='BlogCategory')
        cls.post1 = Post.objects.create(author=cls.author, category=cls.category, title='Post 1', text='Content 1')
        cls.post2 = Post.objects.create(author=cls.author, category=cls.category, title='Post 2', text='Content 2')
        Favorite.objects.create(user=cls.post_author_user, post=cls.post1)
        Favorite.objects.create(user=cls.post_author_user, post=cls.post2)

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.post_author_user)

    def test_get_my_favorites(self):
        url = reverse('api:my-favorites')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(response.data['results'][0]['title'], 'Post 2')
        self.assertEqual(response.data['results'][1]['title'], 'Post 1')

    def test_ordering(self):
        response = self.client.get(reverse('api:my-favorites'), {'ordering': 'created_at'})
        self.assertEqual(response.data['results'][0]['title'], 'Post 1')

        response = self.client.get(reverse('api:my-favorites'), {'ordering': '-created_at'})
        self.assertEqual(response.data['results'][0]['title'], 'Post 2')


    def test_user_not_authenticated(self):
        self.client = APIClient()
        url = reverse('api:my-favorites')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class MyFeedAPIViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='1X<ISRUkw+tuK', email='em@il.com')

        cls.content_maker = User.objects.create_user(username='testuser2', password='1X<ISRUktuK', email='em@ial.com')
        cls.another_content_maker = User.objects.create_user(username='testuser3', password='1X<ISktuK',
                                                             email='epm@il.com')

        cls.author = Author.objects.create(user=cls.content_maker, bio='Biography')
        cls.another_author = Author.objects.create(user=cls.another_content_maker, bio='Biography')

        cls.category1 = Category.objects.create(title='Category 1')
        cls.category2 = Category.objects.create(title='Category 2')
        cls.category3 = Category.objects.create(title='Category 3')

        cls.post1 = Post.objects.create(author=cls.author, category=cls.category1, title='Post 1', text='Content 1')
        cls.post2 = Post.objects.create(author=cls.author, category=cls.category2, title='Post 2', text='Content 2')
        cls.post3 = Post.objects.create(author=cls.another_author, category=cls.category2, title='Post 3',
                                        text='Content 3')
        cls.post4 = Post.objects.create(author=cls.another_author, category=cls.category3, title='Post 4',
                                        text='Content 4')

        cls.user_category_subscription1 = CategorySubscription.objects.create(subscribed_to=cls.category1,
                                                                              subscriber=cls.user)
        cls.user_category_subscription2 = CategorySubscription.objects.create(subscribed_to=cls.category2,
                                                                              subscriber=cls.user)
        cls.user_user_subscription = UserSubscription.objects.create(subscribed_to=cls.content_maker,
                                                                     subscriber=cls.user)

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_my_feed(self):
        url = reverse('api:my-feed')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)  # post1, post2, post3

    def test_get_my_feed_no_subscriptions(self):
        self.user_category_subscription1.delete()
        self.user_category_subscription2.delete()
        self.user_user_subscription.delete()
        url = reverse('api:my-feed')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_get_my_feed_no_posts(self):
        Post.objects.all().delete()
        url = reverse('api:my-feed')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_ordering(self):
        response = self.client.get(reverse('api:my-feed'), {'ordering': 'created_at'})
        self.assertEqual(response.data['results'][0]['title'], 'Post 1')

        response = self.client.get(reverse('api:my-feed'), {'ordering': '-created_at'})
        self.assertEqual(response.data['results'][0]['title'], 'Post 3')

    def test_user_not_authenticated(self):
        self.client = APIClient()
        url = reverse('api:my-feed')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserSubscribeAPIViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(username='user1', password='1X<ISRUkw+tuK', email='em@il.com')
        cls.user2 = User.objects.create_user(username='user2', password='1X<ISRUkw+tuK', email='em@ail.com')

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user1)

    def test_subscribe_to_user(self):
        url = reverse('api:user-subscribe', kwargs={'pk': self.user2.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['success'], 'You successfully subscribed')

    def test_already_subscribed(self):
        UserSubscription.objects.create(subscriber=self.user1, subscribed_to=self.user2)
        url = reverse('api:user-subscribe', kwargs={'pk': self.user2.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['error'], 'You already subscribed')

    def test_subscribe_user_not_found(self):
        url = reverse('api:user-subscribe', kwargs={'pk': 999})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'Such user does not exist')

    def test_user_not_authenticated(self):
        self.client = APIClient()
        url = reverse('api:user-subscribe', kwargs={'pk': self.user2.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserUnsubscribeAPIViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.subscriber = User.objects.create_user(username='user1', password='1X<ISRUkw+tuK', email='em@il.com')
        cls.user2 = User.objects.create_user(username='user2', password='1X<ISRUkw+tuK', email='em@ail.com')

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.subscriber)

    def test_unsubscribe_user(self):
        UserSubscription.objects.create(subscriber=self.subscriber, subscribed_to=self.user2)
        url = reverse('api:user-unsubscribe', kwargs={'pk': self.user2.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data['success'], 'You successfully unsubscribed')

    def test_user_not_subscribed(self):
        url = reverse('api:user-unsubscribe', kwargs={'pk': self.user2.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'Subscription does not exist')

    def test_unsubscribe_user_not_exists(self):
        url = reverse('api:user-unsubscribe', kwargs={'pk': 999})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'Such user does not exist')

    def test_user_not_authenticated(self):
        self.client = APIClient()
        url = reverse('api:user-unsubscribe', kwargs={'pk': self.user2.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CategorySubscribeAPIViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.subscriber = User.objects.create_user(username='user1', password='1X<ISRUkw+tuK', email='em@il.com')
        cls.category1 = Category.objects.create(title='Category 1')
        cls.category2 = Category.objects.create(title='Category 2')

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.subscriber)

    def test_subscribe_to_category(self):
        self.client.force_authenticate(user=self.subscriber)
        url = reverse('api:category-subscribe', kwargs={'pk': self.category1.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['success'], 'You successfully subscribed')

    def test_already_subscribed(self):
        CategorySubscription.objects.create(subscriber=self.subscriber, subscribed_to=self.category1)
        url = reverse('api:category-subscribe', kwargs={'pk': self.category1.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['error'], 'You already subscribed')

    def test_subscribe_category_not_found(self):
        url = reverse('api:category-subscribe', kwargs={'pk': 999})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'There is no such category')

    def test_user_not_authenticated(self):
        self.client = APIClient()
        url = reverse('api:category-subscribe', kwargs={'pk': self.category1.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CategoryUnsubscribeAPIViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category1 = Category.objects.create(title='Category 1')
        cls.user = User.objects.create_user(username='user', password='1X<ISRUkw+tuK', email='em@il.com')

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_unsubscribe_category(self):
        CategorySubscription.objects.create(subscriber=self.user, subscribed_to=self.category1)
        url = reverse('api:category-unsubscribe', kwargs={'pk': self.category1.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data['success'], 'You successfully unsubscribed')

    def test_unsubscribe_category_not_subscribed(self):
        url = reverse('api:category-unsubscribe', kwargs={'pk': self.category1.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'Subscription does not exist')

    def test_unsubscribe_category_not_found(self):
        url = reverse('api:category-unsubscribe', kwargs={'pk': 999})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'There is no such category')

    def test_user_not_authenticated(self):
        self.client = APIClient()
        url = reverse('api:category-unsubscribe', kwargs={'pk': self.category1.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class MyUserSubscriptionsAPIViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.subscriber = User.objects.create_user(username='user1', password='1X<ISRUkw+tuK', email='em@il.com')
        cls.user2 = User.objects.create_user(username='user2', password='1X<ISRUkw+tuK', email='em@ail.com')
        cls.user3 = User.objects.create_user(username='user3', password='1X<ISRUkw+tuK', email='em@iaal.com')
        UserSubscription.objects.create(subscriber=cls.subscriber, subscribed_to=cls.user2)

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.subscriber)

    def test_get_user_subscriptions(self):
        url = reverse('api:my-user-subscriptions')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['username'], 'user2')

    def test_get_user_subscriptions_not_subscribed(self):
        self.client.force_authenticate(user=self.user3)
        url = reverse('api:my-user-subscriptions')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_user_not_authenticated(self):
        self.client.logout()
        url = reverse('api:my-user-subscriptions')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class MyCategoriesSubscriptionsAPIViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.subcriber = User.objects.create_user(username='user', password='1X<ISRUkw+tuK', email='em@il.com')
        cls.non_subcriber = User.objects.create_user(username='user2', password='1X<ISRUkw+tuK', email='em@ail.com')
        cls.category1 = Category.objects.create(title='Category 1')
        cls.category2 = Category.objects.create(title='Category 2')
        CategorySubscription.objects.create(subscriber=cls.subcriber, subscribed_to=cls.category1)

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.subcriber)

    def test_get_categories_subscriptions(self):
        url = reverse('api:my-categories-subscriptions')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['category_title'], 'Category 1')

    def test_get_categories_subscriptions_not_subscribed(self):
        self.client.force_authenticate(user=self.non_subcriber)
        url = reverse('api:my-categories-subscriptions')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_user_not_authenticated(self):
        self.client.logout()
        url = reverse('api:my-categories-subscriptions')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
