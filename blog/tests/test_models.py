from datetime import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase

from blog.models import Author, Post, Category, Comment
from rating.models import PostRating, Vote, CommentRating

User = get_user_model()


class AuthorModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK', email='em@il.com')
        Author.objects.create(user=user, bio='Biography.')

    def test_bio_label(self):
        author = Author.objects.get(pk=1)
        bio_label = author._meta.get_field('bio').verbose_name
        return self.assertEqual(bio_label, 'Biography')

    def test_bio_max_length_is_1000(self):
        author = Author.objects.get(pk=1)
        bio_max_length = author._meta.get_field('bio').max_length
        return self.assertEqual(bio_max_length, 1000)

    def test_user_label(self):
        author = Author.objects.get(pk=1)
        user_label = author._meta.get_field('user').verbose_name
        return self.assertEqual(user_label, 'user')

    def test_author_name_is_username(self):
        author = Author.objects.get(pk=1)
        username = author.user.username
        return self.assertEqual(str(author), username)


class PostModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK', email='em@il.com')
        cls.author = Author.objects.create(user=cls.user, bio='Biography.')
        cls.category = Category.objects.create(title='Category.')
        cls.first_post = Post.objects.create(author=cls.author, category=cls.category, title='First', text='...')
        Post.objects.create(author=cls.author, category=cls.category, title='Second', text='...')
        Post.objects.create(author=cls.author, category=cls.category, title='Third', text='...')

    def test_verbose_names(self):
        post = self.first_post
        field_verboses = {
            'author': 'author',
            'created_at': 'created at',
            'updated_at': 'updated at',
            'title': 'title',
            'text': 'text',
            'category': 'category',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(post._meta.get_field(field).verbose_name, expected_value)

    def test_title_max_length_is_100(self):
        max_length = self.first_post._meta.get_field('title').max_length
        return self.assertEqual(max_length, 100)

    def test_text_max_length_is_3000(self):
        max_length = self.first_post._meta.get_field('text').max_length
        return self.assertEqual(max_length, 3000)

    def test_get_absolute_url(self):
        post = self.first_post
        return self.assertEqual(post.get_absolute_url(), '/blog/1/')

    def test_post_name_is_title(self):
        post = self.first_post
        return self.assertEqual(str(post), post.title)

    def test_ordering(self):
        posts = Post.objects.all()[:3]
        for day, post in enumerate(posts, 1):
            post.created_at = datetime(2024, 1, day, 12, 0, 0)
        expected_ordering = [posts[2], posts[1], posts[0]]

        for index, post in enumerate(expected_ordering):
            self.assertEqual(post, expected_ordering[index])

    def test_comments_count_property(self):
        post = self.first_post
        comments = post.comments.all()
        return self.assertEqual(post.comments_count, len(comments))

    def test_fav_count_property(self):
        post = self.first_post
        favs = post.favorites.all()
        return self.assertEqual(post.fav_count, len(favs))

    def test_save_method_creates_post_rating(self):
        # Creating a new post
        new_post = Post(author=self.author, category=self.category, title='New Post', text='New post content')

        # Checking that PostRating hasn't been created yet. By default, we already have 3 posts.
        self.assertEqual(PostRating.objects.count(), 3)
        new_post.save()
        self.assertEqual(PostRating.objects.count(), 4)

        # Checking the details of the created PostRating
        post_rating = PostRating.objects.filter(obj=new_post).get()
        self.assertEqual(post_rating.obj, new_post)
        self.assertEqual(post_rating.owner, self.user)
        self.assertEqual(post_rating.vote, Vote.VoteType.NEUTRAL)

        # Checking that saving again doesn't create a new PostRating
        new_post.title = 'Updated Title'
        new_post.save()
        self.assertEqual(PostRating.objects.count(), 4)


class CategoryModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(title='Games')

    def test_title_verbose_name(self):
        verbose_name = self.category._meta.get_field('title').verbose_name
        return self.assertEqual(verbose_name, 'title')

    def test_title_max_length_is_30(self):
        max_length = self.category._meta.get_field('title').max_length
        return self.assertEqual(max_length, 30)

    def test_category_name_is_title(self):
        category = self.category
        return self.assertEqual(str(category), category.title)


class CommentModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK', email='em@il.com')
        author = Author.objects.create(user=cls.user, bio='Biography.')
        category = Category.objects.create(title='Category.')
        cls.post = Post.objects.create(author=author, title='First', text='...', category=category)
        cls.first_comment = Comment.objects.create(author=cls.user, post=cls.post, text='FirstComm')
        Comment.objects.create(author=cls.user, post=cls.post, text='SecondComm')
        cls.regexp_comment = Comment.objects.create(author=cls.user, post=cls.post, text='<b>ThirdComm</b>')

    def test_verbose_names(self):
        comment = self.first_comment
        field_verboses = {
            'author': 'author',
            'blog': 'blog',
            'created_at': 'created_at',
            'updated_at': 'updated_at',
            'text': 'text'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                return self.assertEqual(comment._meta.get_field(field).verbose_name, expected_value)

    def test_text_max_length_is_400(self):
        max_length = self.first_comment._meta.get_field('text').max_length
        return self.assertEqual(max_length, 600)

    def test_ordering(self):
        comments = Comment.objects.all()[:3]
        for day, comment in enumerate(comments, 1):
            comment.created_at = datetime(2024, 1, day, 12, 0, 0)
        expected_ordering = [comments[2], comments[1], comments[0]]

        for index, comment in enumerate(expected_ordering):
            self.assertEqual(comment, expected_ordering[index])

    def test_str_regex(self):
        comment = self.regexp_comment
        return self.assertEqual(str(comment), 'ThirdComm')

    def test_save_method_creates_comment_rating(self):
        # Creating a new comment
        new_comment = Comment(author=self.user, post=self.post, text='New comment')

        # Checking that CommentRating hasn't been created yet. By default, we already have 3 comments.
        self.assertEqual(CommentRating.objects.count(), 3)
        new_comment.save()
        self.assertEqual(CommentRating.objects.count(), 4)

        # Checking the details of the created CommentRating
        comment_rating = CommentRating.objects.filter(obj=new_comment).get()
        self.assertEqual(comment_rating.obj, new_comment)
        self.assertEqual(comment_rating.owner, self.user)
        self.assertEqual(comment_rating.vote, Vote.VoteType.NEUTRAL)

        # Checking that saving again doesn't create a new CommentRating
        new_comment.title = 'Updated Title'
        new_comment.save()
        self.assertEqual(CommentRating.objects.count(), 4)
