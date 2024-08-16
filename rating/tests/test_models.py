from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.test import TestCase

from blog.models import Comment, Post, Author, Category
from rating.models import CommentRating, PostRating

User = get_user_model()


class CommentRatingModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK', email='em@il.com')
        cls.another_user = User.objects.create_user(username='testuser2', password='1X<ISRUkw+tuK', email='em@ial.com')
        cls.author = Author.objects.create(user=cls.user, bio='Biography')
        cls.category = Category.objects.create(title='BlogCategory')
        cls.post = Post.objects.create(author=cls.author, category=cls.category, title='Post 1', text='Content 1')
        cls.comment = Comment.objects.create(author=cls.user, post=cls.post, text='Com(t)ent 1')
        cls.comment_rating = CommentRating.objects.create(owner=cls.another_user, obj=cls.comment, vote=1)

    def test_vote_label(self):
        vote_label = self.comment_rating._meta.get_field('vote').verbose_name
        self.assertEqual(vote_label, 'vote')

    def test_owner_label(self):
        owner_label = self.comment_rating._meta.get_field('owner').verbose_name
        self.assertEqual(owner_label, 'owner')

    def test_obj_label(self):
        obj_label = self.comment_rating._meta.get_field('obj').verbose_name
        self.assertEqual(obj_label, 'obj')

    def test_vote_default_choices(self):
        choices = dict(CommentRating.VoteType.choices)
        self.assertEqual(choices[1], 'Like')
        self.assertEqual(choices[0], 'Neutral')
        self.assertEqual(choices[-1], 'Dislike')

    def test_unique_constraint(self):
        with self.assertRaises(IntegrityError):
            CommentRating.objects.create(owner=self.another_user, obj=self.comment, vote=-1)


class PostRatingModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK', email='em@il.com')
        cls.another_user = User.objects.create_user(username='testuser2', password='1X<ISRUkw+tuK', email='em@ail.com')
        cls.author = Author.objects.create(user=cls.user, bio='Biography')
        cls.category = Category.objects.create(title='BlogCategory')
        cls.post = Post.objects.create(author=cls.author, category=cls.category, title='Post 1', text='Content 1')
        cls.post_rating = PostRating.objects.create(owner=cls.another_user, obj=cls.post, vote=1)

    def test_vote_label(self):
        vote_label = self.post_rating._meta.get_field('vote').verbose_name
        self.assertEqual(vote_label, 'vote')

    def test_owner_label(self):
        owner_label = self.post_rating._meta.get_field('owner').verbose_name
        self.assertEqual(owner_label, 'owner')

    def test_obj_label(self):
        obj_label = self.post_rating._meta.get_field('obj').verbose_name
        self.assertEqual(obj_label, 'obj')

    def test_vote_default_choices(self):
        choices = dict(PostRating.VoteType.choices)
        self.assertEqual(choices[1], 'Like')
        self.assertEqual(choices[0], 'Neutral')
        self.assertEqual(choices[-1], 'Dislike')

    def test_unique_constraint(self):
        with self.assertRaises(IntegrityError):
            PostRating.objects.create(owner=self.another_user, obj=self.post, vote=-1)
