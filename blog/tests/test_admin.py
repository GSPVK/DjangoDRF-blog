from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.test import TestCase

from blog.admin import AuthorAdmin, CategoryAdmin, PostAdmin, CommentAdmin
from blog.models import Author, Post, Category, Comment
from rating.models import PostRating
from subscription.models import Favorite

User = get_user_model()


class AuthorAdminTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK', email='em@il.com')
        cls.other_user = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD', email='em@ail.com')
        cls.author = Author.objects.create(user=cls.user, bio='Biography')
        cls.other_author = Author.objects.create(user=cls.other_user, bio='Other Biography')
        cls.category = Category.objects.create(title='BlogCategory')
        cls.category2 = Category.objects.create(title='TestCategory2')
        cls.site = AdminSite()

    def setUp(self):
        self.client.force_login(self.user)

    def test_posts_total(self):
        model_admin = AuthorAdmin(Author, self.site)
        self.assertEqual(model_admin.posts_total(self.author), 0)
        Post.objects.create(author=self.author, category=self.category, title='Post 1', text='Content 1')
        Post.objects.create(author=self.author, category=self.category2, title='Post 2', text='Content 2')
        Post.objects.create(author=self.other_author, category=self.category2, title='Post 2', text='Content 2')
        self.assertEqual(model_admin.posts_total(self.author), 2)


class CategoryAdminTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK', email='em@il.com')
        cls.author = Author.objects.create(user=cls.user, bio='Biography')
        cls.category = Category.objects.create(title='BlogCategory')
        cls.site = AdminSite()

    def test_posts_total(self):
        model_admin = CategoryAdmin(Category, self.site)
        self.assertEqual(model_admin.posts_total(self.category), 0)
        Post.objects.create(author=self.author, category=self.category, title='Post 1', text='Content 1')
        Post.objects.create(author=self.author, category=self.category, title='Post 2', text='Content 2')
        self.assertEqual(model_admin.posts_total(self.category), 2)


class PostAdminTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK', email='em@il.com')
        cls.another_user = User.objects.create_user(username='testuser2', password='1X<ISRUkw+tuK', email='em@ial.com')
        cls.author = Author.objects.create(user=cls.user, bio='Biography')
        cls.category = Category.objects.create(title='BlogCategory')
        cls.post = Post.objects.create(author=cls.author, category=cls.category, title='Post 1', text='Content 1')
        cls.site = AdminSite()

    def setUp(self):
        self.client.force_login(self.user)
        self.request = self.client.request()

    def test_rating_and_fav_count(self):
        model_admin = PostAdmin(Post, self.site)
        obj = model_admin.get_queryset(self.request).get(id=self.post.id)
        self.assertEqual(model_admin.rating(obj), 0)
        self.assertEqual(model_admin.fav_count(obj), 0)

        # When a post is created, a rating of 0 is automatically assigned to the author.
        PostRating.objects.filter(obj=self.post, owner=self.user).update(vote=1)
        PostRating.objects.create(obj=self.post, owner=self.another_user, vote=1)
        Favorite.objects.create(user=self.user, post=self.post)

        obj = model_admin.get_queryset(self.request).get(id=self.post.id)
        self.assertEqual(model_admin.rating(obj), 2)
        self.assertEqual(model_admin.fav_count(obj), 1)


class CommentAdminTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK', email='em@il.com')
        cls.author = Author.objects.create(user=cls.user, bio='Biography')
        cls.category = Category.objects.create(title='BlogCategory')
        cls.post = Post.objects.create(author=cls.author, category=cls.category, title='Post 1', text='Content 1')
        cls.comment = Comment.objects.create(author=cls.user, post=cls.post, text='Com(t)ent 1')
        cls.site = AdminSite()

    def setUp(self):
        self.client.force_login(self.user)
        self.request = self.client.request()

    def test_short_text_and_post_link(self):
        model_admin = CommentAdmin(Comment, self.site)
        obj = model_admin.get_queryset(self.request).get(id=self.comment.id)
        self.assertEqual(model_admin.short_text(obj), 'Com(t)ent 1')
        link = model_admin.post_link(obj)
        self.assertIn('/admin/blog/post/', link)
        self.assertIn(str(self.post.pk), link)
