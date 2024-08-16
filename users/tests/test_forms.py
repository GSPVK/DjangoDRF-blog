from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase

from users.forms import UserForm, ProfileForm, UserProfileForm, CreationForm
from users.models import Profile

User = get_user_model()


class UserFormTest(TestCase):
    def test_valid_form(self):
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'em@ail.com',
            'phone_number': '+79788977898'
        }
        form = UserForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'invalid@email',
            'phone_number': '123'  # Invalid phone number
        }
        form = UserForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn('phone_number', form.errors)


class ProfileFormTest(TestCase):
    def test_valid_form(self):
        data = {
            'telegram_id': '@durov'
        }
        form = ProfileForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        data = {
            'telegram_id': 'a' * 31  # Too long (max_length is 30)
        }
        form = ProfileForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('telegram_id', form.errors)


class UserProfileFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='em@il.com',
            password='testpass123'
        )
        self.profile = Profile.objects.get(user=self.user)

    def test_valid_form(self):
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'phone_number': '+79788977898',
            'email': 'em@ail.com',
            'telegram_id': 'durov',
            'photo': 'profile_photos/no-ava.png'
        }
        form = UserProfileForm(data=data, instance=self.user)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'invalid@email',
            'phone_number': '123',
            'telegram_id': 'a' * 31,
            'photo': 'profile_photos/no-ava.png'
        }
        form = UserProfileForm(data=data, instance=self.user)
        self.assertFalse(form.is_valid())


class CreationFormTest(TestCase):
    def setUp(self):
        Group.objects.create(name='Readers')
        Group.objects.create(name='Bloggers')

    def test_valid_form(self):
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'username': 'testuser',
            'user_group': 'Readers',
            'email': 'em@il.com',
            'phone_number': '+79788977898',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        form = CreationForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'username': 'testuser',
            'user_group': 'InvalidGroup',
            'email': 'invalid@email',
            'phone_number': '123',
            'password1': 'testpass123',
            'password2': 'differentpass123'
        }
        form = CreationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('user_group', form.errors)
        self.assertIn('email', form.errors)
        self.assertIn('phone_number', form.errors)
        self.assertIn('password2', form.errors)

    def test_save_method(self):
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'username': 'testuser',
            'user_group': 'Readers',
            'email': 'em@il.com',
            'phone_number': '+79788977898',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        form = CreationForm(data=data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'em@il.com')
        self.assertEqual(str(user.phone_number), '+79788977898')
        self.assertTrue(user.check_password('testpass123'))
        self.assertTrue(user.groups.filter(name='Readers').exists())


# class CustomUserChangeFormTest(TestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(
#             username='testuser',
#             email='em@il.com',
#             password='testpass123'
#         )
#
#     def test_form_fields(self):
#         form = CustomUserChangeForm(instance=self.user)
#         self.assertIn('username', form.fields)
#         self.assertIn('email', form.fields)
#         self.assertIn('first_name', form.fields)
#         self.assertIn('last_name', form.fields)
#         self.assertIn('phone_number', form.fields)
#
#     def test_changing_user_data(self):
#         data = {
#             'username': 'newusername',
#             'email': 'newemail@example.com',
#             'first_name': 'New',
#             'last_name': 'Name',
#             'phone_number': '+79788977898'
#         }
#         form = CustomUserChangeForm(data=data, instance=self.user)
#         self.assertTrue(form.is_valid())
#         updated_user = form.save()
#         self.assertEqual(updated_user.username, 'newusername')
#         self.assertEqual(updated_user.email, 'newemail@example.com')
#         self.assertEqual(updated_user.first_name, 'New')
#         self.assertEqual(updated_user.last_name, 'Name')
#         self.assertEqual(str(updated_user.phone_number), '+79788977898')
