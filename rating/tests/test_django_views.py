from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from blog.models import Author, Category, Comment, Post
from rating.models import CommentRating, PostRating, Vote

User = get_user_model()


class ChangePostRatingViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.post_author_user = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK', email='em@il.com')
        cls.user_who_rates = User.objects.create_user(username='testuser2', password='1X<ISRUkw+tuK', email='em@ial.com')
        cls.author = Author.objects.create(user=cls.post_author_user, bio='Biography')
        cls.category = Category.objects.create(title='BlogCategory')

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.user_who_rates)
        self.post = Post.objects.create(author=self.author, category=self.category, title='Post 1', text='Content 1')

    def test_post_like_initial(self):
        response = self.client.get(reverse('rating:post-rating', args=[self.post.pk, 'LIKE']))
        self.assertEqual(response.status_code, 302)
        post_rating = PostRating.objects.get(obj=self.post, owner=self.user_who_rates)
        self.assertEqual(post_rating.vote, Vote.VoteType.LIKE.value)

    def test_post_like_toggle_to_neutral(self):
        self.client.get(reverse('rating:post-rating', args=[self.post.pk, 'LIKE']))
        post_rating = PostRating.objects.get(obj=self.post, owner=self.user_who_rates)
        self.assertEqual(post_rating.vote, Vote.VoteType.LIKE.value)

        response = self.client.get(reverse('rating:post-rating', args=[self.post.pk, 'LIKE']))
        self.assertEqual(response.status_code, 302)
        post_rating.refresh_from_db()
        self.assertEqual(post_rating.vote, Vote.VoteType.NEUTRAL.value)

    def test_post_dislike_initial(self):
        response = self.client.get(reverse('rating:post-rating', args=[self.post.pk, 'DISLIKE']))
        self.assertEqual(response.status_code, 302)
        post_rating = PostRating.objects.get(obj=self.post, owner=self.user_who_rates)
        self.assertEqual(post_rating.vote, Vote.VoteType.DISLIKE.value)

    def test_post_dislike_toggle_to_neutral(self):
        self.client.get(reverse('rating:post-rating', args=[self.post.pk, 'DISLIKE']))
        post_rating = PostRating.objects.get(obj=self.post, owner=self.user_who_rates)
        self.assertEqual(post_rating.vote, Vote.VoteType.DISLIKE.value)

        response = self.client.get(reverse('rating:post-rating', args=[self.post.pk, 'DISLIKE']))
        self.assertEqual(response.status_code, 302)
        post_rating.refresh_from_db()
        self.assertEqual(post_rating.vote, Vote.VoteType.NEUTRAL.value)

    def test_change_current_vote(self):
        response = self.client.get(reverse('rating:post-rating', args=[self.post.pk, 'DISLIKE']))
        self.assertEqual(response.status_code, 302)
        post_rating = PostRating.objects.get(obj=self.post, owner=self.user_who_rates)
        self.assertEqual(post_rating.vote, Vote.VoteType.DISLIKE.value)

        response = self.client.get(reverse('rating:post-rating', args=[self.post.pk, 'LIKE']))
        self.assertEqual(response.status_code, 302)
        post_rating = PostRating.objects.get(obj=self.post, owner=self.user_who_rates)
        self.assertEqual(post_rating.vote, Vote.VoteType.LIKE.value)

    def test_invalid_vote_type(self):
        response = self.client.get(reverse('rating:post-rating', args=[self.post.pk, 'INVALID']))
        self.assertEqual(response.status_code, 400)

    def test_not_logged_in(self):
        self.client.logout()
        response = self.client.get(reverse('rating:post-rating', args=[self.post.pk, 'LIKE']))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_redirects_to_next_page(self):
        next_url = reverse('blog:post-detail', args=[self.post.pk])
        response = self.client.get(reverse('rating:post-rating', args=[self.post.pk, 'LIKE']) + f'?next={next_url}')
        self.assertRedirects(response, next_url)


class ChangeCommentRatingViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.post_author_user = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK', email='em@il.com')
        cls.user_who_rates = User.objects.create_user(username='testuser2', password='1X<ISRUkw+tuK', email='em@ial.com')
        cls.author = Author.objects.create(user=cls.post_author_user, bio='Biography')
        cls.category = Category.objects.create(title='BlogCategory')
        cls.post = Post.objects.create(author=cls.author, category=cls.category, title='Post 1', text='Content 1')

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.user_who_rates)
        self.comment = Comment.objects.create(author=self.post_author_user, post=self.post, text='Com(t)ent 1')

    def test_comment_like_initial(self):
        response = self.client.get(reverse('rating:comment-rating', args=[self.post.pk, self.comment.pk, 'LIKE']))
        self.assertEqual(response.status_code, 302)
        comment_rating = CommentRating.objects.get(obj=self.comment, owner=self.user_who_rates)
        self.assertEqual(comment_rating.vote, Vote.VoteType.LIKE.value)

    def test_comment_like_toggle_to_neutral(self):
        self.client.get(reverse('rating:comment-rating', args=[self.post.pk, self.comment.pk, 'LIKE']))
        comment_rating = CommentRating.objects.get(obj=self.comment, owner=self.user_who_rates)
        self.assertEqual(comment_rating.vote, Vote.VoteType.LIKE.value)

        response = self.client.get(reverse('rating:comment-rating', args=[self.post.pk, self.comment.pk, 'LIKE']))
        self.assertEqual(response.status_code, 302)
        comment_rating.refresh_from_db()
        self.assertEqual(comment_rating.vote, Vote.VoteType.NEUTRAL.value)

    def test_comment_dislike_initial(self):
        response = self.client.get(reverse('rating:comment-rating', args=[self.post.pk, self.comment.pk, 'DISLIKE']))
        self.assertEqual(response.status_code, 302)
        comment_rating = CommentRating.objects.get(obj=self.comment, owner=self.user_who_rates)
        self.assertEqual(comment_rating.vote, Vote.VoteType.DISLIKE.value)

    def test_comment_dislike_toggle_to_neutral(self):
        self.client.get(reverse('rating:comment-rating', args=[self.post.pk, self.comment.pk, 'DISLIKE']))
        comment_rating = CommentRating.objects.get(obj=self.comment, owner=self.user_who_rates)
        self.assertEqual(comment_rating.vote, Vote.VoteType.DISLIKE.value)

        response = self.client.get(reverse('rating:comment-rating', args=[self.post.pk, self.comment.pk, 'DISLIKE']))
        self.assertEqual(response.status_code, 302)
        comment_rating.refresh_from_db()
        self.assertEqual(comment_rating.vote, Vote.VoteType.NEUTRAL.value)

    def test_change_current_vote(self):
        self.client.get(reverse('rating:comment-rating', args=[self.post.pk, self.comment.pk, 'DISLIKE']))
        comment_rating = CommentRating.objects.get(obj=self.comment, owner=self.user_who_rates)
        self.assertEqual(comment_rating.vote, Vote.VoteType.DISLIKE.value)

        response = self.client.get(reverse('rating:comment-rating', args=[self.post.pk, self.comment.pk, 'LIKE']))
        self.assertEqual(response.status_code, 302)
        comment_rating.refresh_from_db()
        self.assertEqual(comment_rating.vote, Vote.VoteType.LIKE.value)

    def test_invalid_vote_type(self):
        response = self.client.get(reverse('rating:comment-rating', args=[self.post.pk, self.comment.pk, 'INVALID']))
        self.assertEqual(response.status_code, 400)

    def test_not_logged_in(self):
        self.client.logout()
        response = self.client.get(reverse('rating:comment-rating', args=[self.post.pk, self.comment.pk, 'LIKE']))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

    def test_redirects_to_next_page(self):
        next_url = reverse('blog:post-detail', args=[self.post.pk])
        response = self.client.get(
            reverse('rating:comment-rating', args=[self.post.pk, self.comment.pk, 'LIKE']) + f'?next={next_url}')
        self.assertRedirects(response, next_url)
