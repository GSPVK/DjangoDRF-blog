from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from blog.models import Author, Category, Comment, Post
from rating.models import Vote, CommentRating, PostRating

User = get_user_model()


class PostLikeDislikeAPIViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.post_author_user = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK',
                                                        email='em@il.com')
        cls.user_who_rates = User.objects.create_user(username='testuser2', password='1X<ISRUkw+tuK',
                                                      email='em@ial.com')
        cls.author = Author.objects.create(user=cls.post_author_user, bio='Biography')
        cls.category = Category.objects.create(title='BlogCategory')

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user_who_rates)
        self.post = Post.objects.create(author=self.author, category=self.category, title='Post 1', text='Content 1')

    def test_post_like_initial(self):
        url = reverse('api:post-like', kwargs={'pk': self.post.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['success'], 'Post liked successfully')
        post_rating = PostRating.objects.get(obj=self.post, owner=self.user_who_rates)
        self.assertEqual(post_rating.vote, Vote.VoteType.LIKE.value)

    def test_post_like_toggle_to_neutral(self):
        url = reverse('api:post-like', kwargs={'pk': self.post.pk})
        self.client.post(url)
        post_rating = PostRating.objects.get(obj=self.post, owner=self.user_who_rates)
        self.assertEqual(post_rating.vote, Vote.VoteType.LIKE.value)

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], 'Like from post removed successfully')
        post_rating.refresh_from_db()
        self.assertEqual(post_rating.vote, Vote.VoteType.NEUTRAL.value)

    def test_post_dislike_initial(self):
        url = reverse('api:post-dislike', kwargs={'pk': self.post.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['success'], 'Post disliked successfully')
        post_rating = PostRating.objects.get(obj=self.post, owner=self.user_who_rates)
        self.assertEqual(post_rating.vote, Vote.VoteType.DISLIKE.value)

    def test_post_dislike_toggle_to_neutral(self):
        url = reverse('api:post-dislike', kwargs={'pk': self.post.pk})
        self.client.post(url)
        post_rating = PostRating.objects.get(obj=self.post, owner=self.user_who_rates)
        self.assertEqual(post_rating.vote, Vote.VoteType.DISLIKE.value)

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], 'Dislike from post removed successfully')
        post_rating.refresh_from_db()
        self.assertEqual(post_rating.vote, Vote.VoteType.NEUTRAL.value)

    def test_change_current_vote(self):
        url = reverse('api:post-like', kwargs={'pk': self.post.pk})
        self.client.post(url)
        post_rating = PostRating.objects.get(obj=self.post, owner=self.user_who_rates)
        self.assertEqual(post_rating.vote, Vote.VoteType.LIKE.value)

        url = reverse('api:post-dislike', kwargs={'pk': self.post.pk})
        response = self.client.post(url)
        post_rating.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], 'Post disliked successfully')
        self.assertEqual(post_rating.vote, Vote.VoteType.DISLIKE.value)

    def test_post_invalid_vote(self):
        url = reverse('api:post-like', kwargs={'pk': 99999})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_not_logged_in(self):
        self.client.logout()
        url = reverse('api:post-like', kwargs={'pk': self.post.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CommentLikeDislikeAPIViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.post_author_user = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK',
                                                        email='em@il.com')
        cls.user_who_rates = User.objects.create_user(username='testuser2', password='1X<ISRUkw+tuK',
                                                      email='em@ial.com')
        cls.author = Author.objects.create(user=cls.post_author_user, bio='Biography')
        cls.category = Category.objects.create(title='BlogCategory')
        cls.post = Post.objects.create(author=cls.author, category=cls.category, title='Post 1', text='Content 1')

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user_who_rates)
        self.comment = Comment.objects.create(author=self.post_author_user, post=self.post, text='Com(t)ent 1')

    def test_comment_like_initial(self):
        url = reverse('api:comment-like', kwargs={'pk': self.comment.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['success'], 'Comment liked successfully')
        comment_rating = CommentRating.objects.get(obj=self.comment, owner=self.user_who_rates)
        self.assertEqual(comment_rating.vote, Vote.VoteType.LIKE.value)

    def test_comment_like_toggle_to_neutral(self):
        url = reverse('api:comment-like', kwargs={'pk': self.comment.pk})
        # Лайкнем комментарий сначала
        self.client.post(url)
        comment_rating = CommentRating.objects.get(obj=self.comment, owner=self.user_who_rates)
        self.assertEqual(comment_rating.vote, Vote.VoteType.LIKE.value)

        # Затем повторно лайкнем, и убедимся, что рейтинг становится нейтральным
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], 'Like from comment removed successfully')
        comment_rating.refresh_from_db()
        self.assertEqual(comment_rating.vote, Vote.VoteType.NEUTRAL.value)

    def test_comment_dislike_initial(self):
        url = reverse('api:comment-dislike', kwargs={'pk': self.comment.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['success'], 'Comment disliked successfully')
        comment_rating = CommentRating.objects.get(obj=self.comment, owner=self.user_who_rates)
        self.assertEqual(comment_rating.vote, Vote.VoteType.DISLIKE.value)

    def test_comment_dislike_toggle_to_neutral(self):
        url = reverse('api:comment-dislike', kwargs={'pk': self.comment.pk})
        self.client.post(url)
        comment_rating = CommentRating.objects.get(obj=self.comment, owner=self.user_who_rates)
        self.assertEqual(comment_rating.vote, Vote.VoteType.DISLIKE.value)

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], 'Dislike from comment removed successfully')
        comment_rating.refresh_from_db()
        self.assertEqual(comment_rating.vote, Vote.VoteType.NEUTRAL.value)

    def test_change_current_vote(self):
        url = reverse('api:comment-like', kwargs={'pk': self.comment.pk})
        self.client.post(url)
        comment_rating = CommentRating.objects.get(obj=self.comment, owner=self.user_who_rates)
        self.assertEqual(comment_rating.vote, Vote.VoteType.LIKE.value)

        url = reverse('api:comment-dislike', kwargs={'pk': self.comment.pk})
        response = self.client.post(url)
        comment_rating.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], 'Comment disliked successfully')
        self.assertEqual(comment_rating.vote, Vote.VoteType.DISLIKE.value)

    def test_comment_invalid_vote(self):
        url = reverse('api:comment-like', kwargs={'pk': 99999})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_comment_not_logged_in(self):
        self.client.logout()
        url = reverse('api:comment-like', kwargs={'pk': self.comment.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
