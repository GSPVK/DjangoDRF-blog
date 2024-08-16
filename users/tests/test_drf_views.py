import io
import shutil
import tempfile

from PIL import Image
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.test.client import encode_multipart
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from blog.models import Post, Comment, Author, Category
from rating.models import CommentRating, PostRating
from subscription.models import UserSubscription

User = get_user_model()


class SignUpAPIViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        Group.objects.create(name='Readers')
        cls.url = reverse('api:signup')

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user(self):
        valid_payload = {
            'username': 'newuser',
            'password': '2HJ1vRV0Z&3iD',
            'password_confirm': '2HJ1vRV0Z&3iD',
            'email': 'em@il.com',
            'user_group': 'Readers',
        }
        response = self.client.post(self.url, valid_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_create_user_invalid_group(self):
        invalid_group_payload = {
            'username': 'newuser',
            'password': '2HJ1vRV0Z&3iD',
            'password_confirm': '2HJ1vRV0Z&3iD',
            'user_group': 'reAders',
            'email': 'em@il.com',
        }
        response = self.client.post(self.url, invalid_group_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_password_not_match(self):
        invalid_password_confirm_payload = {
            'username': 'newuser',
            'password': '2HJ1vRV0Z&3iD',
            'password_confirm': 'passdontmatch',
            'user_group': 'Readers',
            'email': 'em@il.com',
        }
        response = self.client.post(self.url, invalid_password_confirm_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_email_in_use(self):
        email = 'em@il.com'
        User.objects.create_user(username='testuser', email=email, password='2HJ1vRV0Z&3iD')
        email_in_use_payload = {
            'username': 'newuser',
            'password': '2HJ1vRV0Z&3iD',
            'password_confirm': 'passdontmatch',
            'user_group': 'Readers',
            'email': email,
        }
        response = self.client.post(self.url, email_in_use_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ChangePasswordAPIViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', email='em@il.com', password='oldpassword123')
        cls.url = reverse('api:change-password')

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_change_password_success(self):
        payload = {
            'old_pass': 'oldpassword123',
            'new_pass': 'newpassword123',
            'new_pass_confirm': 'newpassword123'
        }
        response = self.client.put(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword123'))

    def test_change_password_wrong_old_password(self):
        payload = {
            'old_pass': 'wrongpassword',
            'new_pass': 'newpassword123',
            'new_pass_confirm': 'newpassword123'
        }
        response = self.client.put(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_passwords_dont_match(self):
        payload = {
            'old_pass': 'oldpassword123',
            'new_pass': 'newpassword123',
            'new_pass_confirm': 'passdontmatch'
        }
        response = self.client.put(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class MeAPIViewTest(APITestCase):
    temp_media_dir = tempfile.mkdtemp()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.temp_media_dir)
        super().tearDownClass()

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', email='em@il.com', password='testpassword123')
        cls.url = reverse('api:me')

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    @staticmethod
    def generate_photo_file():
        file = io.BytesIO()
        image = Image.new('RGB', size=(500, 500), color='red')
        image.save(file, 'png')
        file.name = 'test.png'
        file.seek(0)
        return file

    def test_get_profile(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'em@il.com')
        self.assertEqual(response.data['subscribers_count'], 0)

    def test_user_have_subscribers(self):
        subscriber = User.objects.create_user(username='subscriber', email='subscriber@il.com', password='testpass123')
        UserSubscription.objects.create(subscriber=subscriber, subscribed_to=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'em@il.com')
        self.assertEqual(response.data['subscribers_count'], 1)

    def test_partial_update_profile(self):
        payload = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'newemail@example.com'
        }
        response = self.client.patch(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Test')
        self.assertEqual(self.user.last_name, 'User')
        self.assertEqual(self.user.email, 'newemail@example.com')

    @override_settings(MEDIA_ROOT=temp_media_dir)
    def test_update_profile(self):
        photo_file = self.generate_photo_file()
        data = {
            'first_name': 'New',
            'last_name': 'Name',
            'email': 'newemail@example.com',
            'phone_number': '+79788889868',
            'profile.telegram_id': '',
        }
        files = {
            'profile.photo': SimpleUploadedFile('test.png', photo_file.getvalue(), content_type='image/png')
        }
        boundary = 'BoUnDaRyStRiNg'
        payload = encode_multipart(boundary, {**data, **files})
        response = self.client.put(
            self.url,
            payload,
            content_type=f'multipart/form-data; boundary={boundary}'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'New')
        self.assertEqual(self.user.last_name, 'Name')
        self.assertEqual(self.user.email, 'newemail@example.com')
        self.assertEqual(self.user.phone_number, '+79788889868')
        self.assertEqual(self.user.profile.telegram_id, '')
        self.assertNotEqual(self.user.profile.photo, '')

    def test_unauthenticated_access(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class FullMeAPIViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', email='em@il.com', password='testpassword123')
        cls.author = Author.objects.create(user=cls.user, bio='')
        cls.category = Category.objects.create(title='Test Category')
        cls.post = Post.objects.create(author=cls.author, category=cls.category, title='Test Post', text='Test Content')
        cls.comment = Comment.objects.create(author=cls.user, post=cls.post, text='Test Comment')
        cls.url = reverse('api:me-full')

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_full_profile(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'em@il.com')
        self.assertEqual(response.data['rating'], 0)

    def test_nested_posts_and_comments(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['posts']['count'], 1)
        self.assertEqual(response.data['comments']['count'], 1)
        self.assertEqual(response.data['posts']['results'][0]['title'], 'Test Post')
        self.assertEqual(response.data['comments']['results'][0]['text'], 'Test Comment')

        Post.objects.create(author=self.author, category=self.category, title='Another Post', text='Another Content')
        Comment.objects.create(author=self.user, post=self.post, text='Another Comment')
        response = self.client.get(self.url)
        self.assertEqual(response.data['posts']['count'], 2)
        self.assertEqual(response.data['comments']['count'], 2)

    def test_nested_posts_and_comments_is_paginated(self):
        expected_posts_paginaion = 2
        expected_comments_paginaion = 5
        for i in range(expected_posts_paginaion + 1):
            # remind that last "i" will be equal to "USERS_POSTS_PAGINATE_BY" value
            Post.objects.create(author=self.author, category=self.category, title=f'Another Post {i}',
                                text=f'Another Content {i}')
        for i in range(expected_comments_paginaion + 1):
            Comment.objects.create(author=self.user, post=self.post, text=f'Another Comment {i}')
        posts_count = Post.objects.filter(author=self.author).count()
        comments_count = Comment.objects.filter(author=self.user).count()

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('next', response.data['posts'])
        self.assertIn('next', response.data['comments'])
        self.assertEqual(response.data['posts']['count'], posts_count)
        self.assertEqual(response.data['comments']['count'], comments_count)
        self.assertEqual(len(response.data['posts']['results']), expected_posts_paginaion)
        self.assertEqual(len(response.data['comments']['results']), expected_comments_paginaion)

        response = self.client.get(self.url + '?posts_page=2&comments_page=2')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['posts']['results']), 2)  # one from setUpTestData and other from cycle above
        self.assertEqual(len(response.data['posts']['results']), 2)  # same here

        response = self.client.get(self.url + '?posts_page=22&comments_page=22')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_access(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserProfileAPIViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', email='em@il.com', password='testpassword123')
        cls.other_user = User.objects.create_user(username='otheruser', email='em2@il.com', password='otherpassword123')
        cls.url = reverse('api:user-profile', kwargs={'pk': cls.other_user.pk})

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_user_profile(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'otheruser')
        self.assertEqual(response.data['email'], 'em2@il.com')
        self.assertEqual(response.data['subscribers_count'], 0)

    def test_request_user_subscribed(self):
        UserSubscription.objects.create(subscriber=self.user, subscribed_to=self.other_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['subscribers_count'], 1)
        self.assertTrue(response.data['subscribed'])

    def test_request_user_not_subscribed(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['subscribers_count'], 0)
        self.assertFalse(response.data['subscribed'])

    def test_nonexistent_user(self):
        url = reverse('api:user-profile', kwargs={'pk': 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class FullUserProfileAPIViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', email='em@il.com', password='testpassword123')
        cls.other_user = User.objects.create_user(username='testuser2', email='em2@il.com', password='testpassword123')
        cls.author = Author.objects.create(user=cls.other_user, bio='')
        cls.category = Category.objects.create(title='Test Category')
        cls.post = Post.objects.create(author=cls.author, category=cls.category, title='Test Post', text='Test Content')
        cls.comment = Comment.objects.create(author=cls.other_user, post=cls.post, text='Test Comment')
        cls.url = reverse('api:user-profile-full', kwargs={'pk': cls.other_user.pk})

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_full_user_profile(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser2')
        self.assertEqual(response.data['email'], 'em2@il.com')
        self.assertEqual(response.data['rating'], 0)
        self.assertIn('posts', response.data)
        self.assertIn('comments', response.data)

    def test_nested_posts_and_comments(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['posts']['count'], 1)
        self.assertEqual(response.data['comments']['count'], 1)
        self.assertEqual(response.data['posts']['results'][0]['title'], 'Test Post')
        self.assertEqual(response.data['comments']['results'][0]['text'], 'Test Comment')

    def test_nested_posts_and_comments_is_paginated(self):
        expected_posts_paginaion = 2
        expected_comments_paginaion = 5
        for i in range(expected_posts_paginaion + 1):
            # remind that last "i" will be equal to "USERS_POSTS_PAGINATE_BY" value
            Post.objects.create(author=self.author, category=self.category, title=f'Another Post {i}',
                                text=f'Another Content {i}')
        for i in range(expected_comments_paginaion + 1):
            Comment.objects.create(author=self.other_user, post=self.post, text=f'Another Comment {i}')
        posts_count = Post.objects.filter(author=self.author).count()
        comments_count = Comment.objects.filter(author=self.other_user).count()

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('next', response.data['posts'])
        self.assertIn('next', response.data['comments'])
        self.assertEqual(response.data['posts']['count'], posts_count)
        self.assertEqual(response.data['comments']['count'], comments_count)
        self.assertEqual(len(response.data['posts']['results']), expected_posts_paginaion)
        self.assertEqual(len(response.data['comments']['results']), expected_comments_paginaion)

        response = self.client.get(self.url + '?posts_page=2&comments_page=2')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['posts']['results']), 2)  # one from setUpTestData and other from cycle above
        self.assertEqual(len(response.data['posts']['results']), 2)  # same here

        response = self.client.get(self.url + '?posts_page=22&comments_page=22')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_access(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['subscribed'], False)

    def test_request_user_subscribed(self):
        UserSubscription.objects.create(subscriber=self.user, subscribed_to=self.other_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['subscribers_count'], 1)
        self.assertTrue(response.data['subscribed'])

    def test_request_user_not_subscribed(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['subscribers_count'], 0)
        self.assertFalse(response.data['subscribed'])

    def test_nonexistent_user(self):
        url = reverse('api:user-profile-full', kwargs={'pk': 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_profile_data_included(self):
        self.other_user.profile.telegram_id = '@testuser'
        self.other_user.profile.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['profile']['telegram_id'], '@testuser')

    def test_user_rating_calculation(self):
        PostRating.objects.create(owner=self.user, obj=self.post, vote=1)
        CommentRating.objects.create(owner=self.user, obj=self.comment, vote=1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['rating'], 2)
