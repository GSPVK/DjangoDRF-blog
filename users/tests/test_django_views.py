from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase, Client
from django.urls import reverse

from blog.models import Post, Comment, Author, Category
from rating.models import PostRating

User = get_user_model()


class UserProfileViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK', email='test1@user.com')
        cls.user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD', email='test2@user.com')
        cls.author = Author.objects.create(user=cls.user1, bio='Author Bio')
        cls.category = Category.objects.create(title='BlogCategory')
        cls.post = Post.objects.create(author=cls.author, category=cls.category, title='Post', text='Content')

        cls.client = Client()
        cls.url = reverse('users:profile', kwargs={'pk': cls.user1.pk})

    def setUp(self):
        self.client.force_login(self.user1)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'users/user_detail.html')

    def test_pagination_comments(self):
        expected_paginaion = 5
        for i in range(expected_paginaion + 1):
            Comment.objects.create(post=self.post, author=self.user1, text=f'Comment {i}')
        response = self.client.get(f"{self.url}?comments_page=1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['comments']), expected_paginaion)

    def test_pagination_posts(self):
        expected_paginaion = 2
        for i in range(expected_paginaion + 1):
            Post.objects.create(author=self.author, category=self.category, title=f'Post {i}', text=f'Content {i}')
        response = self.client.get(f"{self.url}?posts_page=1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['posts']), min(2, expected_paginaion))

    def test_rating_calculation(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['rating'], 0)

        PostRating.objects.create(owner=self.user2, obj=self.post, vote=1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['rating'], 1)

    def test_user_not_blogger_exception(self):
        self.client.force_login(self.user2)
        url = reverse('users:profile', kwargs={'pk': self.user2.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['rating'], 0)
        self.assertQuerySetEqual(response.context['posts'], [])


class UserProfileEditViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK', email='em@il.com')
        cls.user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD', email='em@il2.com')
        cls.url = reverse('users:profile-edit', kwargs={'pk': cls.user1.pk})

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.user1)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/user_form.html')

    def test_edit_profile_unauthenticated(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_edit_profile_authenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/user_form.html')

    def test_edit_profile_permission_denied(self):
        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_update_profile(self):
        self.client.post(self.url, {
            'first_name': '',
            'last_name': '',
            'phone_number': '',
            'email': 'em@il.com',
            'telegram_id': 'Durov',
            'photo': 'profile_photos/no-ava.png'
        })
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.profile.telegram_id, 'Durov')


class SignUpViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.signup_url = reverse('users:signup')
        Group.objects.create(name='Readers')

    def setUp(self):
        self.client = Client()

    def test_signup_unauthenticated_access(self):
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/sign_up.html')

    def test_signup_authenticated_redirect(self):
        user = User.objects.create_user(username='testuser', password='1X<ISRUkw+tuK', email='test@user.com')
        self.client.force_login(user)
        response = self.client.get(self.signup_url)
        self.assertRedirects(response, reverse('blog:index'))

    def test_signup_form_submission(self):
        response = self.client.post(self.signup_url, {
            'username': 'newuser',
            'email': 'em@il2.com',
            'password1': '2HJ1vRV0Z&3iD',
            'password2': '2HJ1vRV0Z&3iD',
            'user_group': 'Readers',
            'phone_number': '',
            'first_name': '',
            'last_name': '',
        })
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(User.objects.filter(username='newuser').exists())
