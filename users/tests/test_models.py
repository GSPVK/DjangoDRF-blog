from django.db.utils import IntegrityError
from django.test import TestCase

from subscription.models import UserSubscription
from users.models import User, Profile


class UserModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser',
            email='em@il.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        cls.noname_user = User.objects.create_user(
            username='testuser2',
            email='esm@il.com',
            password='testpass123',
        )

    def test_email_label(self):
        field_label = self.user._meta.get_field('email').verbose_name
        self.assertEqual(field_label, 'email')

    def test_phone_number_label(self):
        field_label = self.user._meta.get_field('phone_number').verbose_name
        self.assertEqual(field_label, 'Phone number')

    def test_fullname_property(self):
        self.assertEqual(self.user.fullname, 'Test User')

    def test_fullname_property_without_first_and_last_names(self):
        self.assertEqual(self.noname_user.fullname, 'No Name')

    def test_firstname_only(self):
        self.firstname_user = User.objects.create_user(
            username='testuser3',
            email='esm@isl.com',
            password='testpass123',
            first_name='Firstname',
        )
        self.assertEqual(self.firstname_user.fullname, 'Firstname')

    def test_lastname_only(self):
        self.lastname_user = User.objects.create_user(
            username='testuser3',
            email='esm@isl.com',
            password='testpass123',
            last_name='Lastname',
        )
        self.assertEqual(self.lastname_user.fullname, 'Lastname')

    def test_subscribers_count_property(self):
        self.assertEqual(self.user.subscribers_count, 0)
        UserSubscription.objects.create(subscriber=self.noname_user, subscribed_to=self.user)
        self.assertEqual(self.user.subscribers_count, 1)

    def test_get_absolute_url(self):
        self.assertEqual(self.user.get_absolute_url(), f'/users/profile/{self.user.pk}/')

    def test_profile_creation(self):
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsInstance(self.user.profile, Profile)

    def test_unique_email(self):
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                username='testuser2',
                email='em@il.com',
                password='testpass123'
            )


class ProfileModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser',
            email='em@il.com',
            password='testpass123'
        )
        cls.profile = cls.user.profile

    def test_user_label(self):
        field_label = self.profile._meta.get_field('user').verbose_name
        self.assertEqual(field_label, 'user')

    def test_telegram_id_label(self):
        field_label = self.profile._meta.get_field('telegram_id').verbose_name
        self.assertEqual(field_label, 'Telegram')

    def test_photo_upload_to(self):
        field = self.profile._meta.get_field('photo')
        self.assertEqual(field.upload_to, 'profile_photos/')

    def test_str_method(self):
        self.assertEqual(str(self.profile), f'{self.user} (id={self.user.pk})')

    def test_get_absolute_url(self):
        self.assertEqual(self.profile.get_absolute_url(), f'/users/profile/{self.user.pk}/')
