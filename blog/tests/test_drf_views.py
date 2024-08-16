from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from blog.api.serializers.endpoints.categories import CategorySerializer
from blog.models import Category, Post, Comment, Author
from subscription.models import CategorySubscription

User = get_user_model()


# Only users in the Bloggers group can create posts, as post creation requires an entry in the
# Authors table. This entry is automatically created (by the "create_or_delete_blog_author" signal)
# when a user is assigned to the Blogger group. Readers cannot create posts because they lack
# an entry in the Authors table.
# Thus, you can create an instance of the Author model by yourself, or by assigning the user to the Bloggers group


class CategoryViewSetTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user(username='admin', password='adminpass', email='em@il.com', is_staff=True)
        cls.user = User.objects.create_user(username='user', password='securepass', email='em@ail.com')
        cls.category1 = Category.objects.create(title='Category 1')
        cls.category2 = Category.objects.create(title='Category 2')

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)

    def test_list_categories(self):
        self.client.logout()
        url = reverse('api:categories-list')
        response = self.client.get(url)
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer.data)

    def test_retrieve_category(self):
        url = reverse('api:categories-detail', kwargs={'pk': self.category1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_category_subscribers_info(self):
        url = reverse('api:categories-detail', kwargs={'pk': self.category1.pk})
        response = self.client.get(url)
        self.assertEqual(response.data['subscribed'], False)
        self.assertEqual(response.data['subscribers'], 0)

        CategorySubscription.objects.create(subscriber=self.admin, subscribed_to=self.category1)
        response = self.client.get(url)
        self.assertEqual(response.data['subscribed'], True)
        self.assertEqual(response.data['subscribers'], 1)

    def test_retrieve_category_posts_count(self):
        url = reverse('api:categories-detail', kwargs={'pk': self.category1.pk})
        response = self.client.get(url)
        self.assertEqual(response.data['posts_count'], 0)

        author = Author.objects.create(user=self.user, bio='Biography.')
        Post.objects.create(author=author, category=self.category1, text='sample text')
        response = self.client.get(url)
        self.assertEqual(response.data['posts_count'], 1)

    def test_admin_create_category(self):
        url = reverse('api:categories-list')
        data = {'title': 'New Category'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 3)
        self.assertEqual(Category.objects.last().title, 'New Category')

    def test_guest_cannot_create_category(self):
        self.client.logout()
        url = reverse('api:categories-list')
        data = {'title': 'New Category'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_category_without_permission(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('api:categories-list')
        data = {'title': 'New Category'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_category(self):
        url = reverse('api:categories-detail', kwargs={'pk': self.category2.pk})
        data = {'title': 'Completely Updated Category 2'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category2.refresh_from_db()
        self.assertEqual(self.category2.title, 'Completely Updated Category 2')

    def test_partial_update_category(self):
        url = reverse('api:categories-detail', kwargs={'pk': self.category1.pk})
        data = {'title': 'Updated Category 1'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.category1.refresh_from_db()
        self.assertEqual(self.category1.title, 'Updated Category 1')

    def test_delete_category(self):
        url = reverse('api:categories-detail', kwargs={'pk': self.category1.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(pk=self.category1.pk).exists())


class PostWCommentsRetrieveAPIViewTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK', email='em@il.com')
        cls.author = Author.objects.create(user=cls.user, bio='Biography.')
        cls.category = Category.objects.create(title='BlogCategory.')
        cls.post = Post.objects.create(author=cls.author, category=cls.category, title='Title', text='...')
        cls.comment1 = Comment.objects.create(post=cls.post, author=cls.user, text='Comment 1')
        with freeze_time(datetime.now() + timedelta(seconds=1)):
            cls.comment2 = Comment.objects.create(post=cls.post, author=cls.user, text='Comment 2')

    def setUp(self):
        self.client = APIClient()

    def test_retrieve_post_with_comments(self):
        url = reverse('api:post-with-comments', kwargs={'pk': self.post.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.post.id)
        self.assertEqual(response.data['title'], self.post.title)
        self.assertEqual(response.data['comments_count'], 2)
        self.assertIn('comments', response.data)
        # blog.models.Comment.Meta.ordering = ('-created_at',)             VVV
        self.assertEqual(response.data['comments']['results'][0]['text'], 'Comment 2')
        self.assertEqual(response.data['comments']['results'][1]['text'], 'Comment 1')

    def test_post_not_found(self):
        url = reverse('api:post-with-comments', kwargs={'pk': 99999})  # Non-existent post
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class PostViewSetTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.blogger = User.objects.create_user(username='testuser', password='testpass', email='em@il.com')
        cls.another_blogger = User.objects.create_user(username='testuser2', password='testpass', email='em@aail.com')
        cls.non_blogger_user = User.objects.create_user(username='testuser3', password='testpass', email='eme@aail.com')
        bloggers = Group.objects.create(name='Bloggers')
        cls.blogger.groups.add(bloggers)  # При присвоении группы Bloggers сигналом создаётся запись в модели Author
        cls.another_blogger.groups.add(bloggers)
        cls.author = Author.objects.get(user=cls.blogger)
        cls.another_author = Author.objects.get(user=cls.another_blogger)
        cls.category = Category.objects.create(title='Test Category')
        cls.empty_category = Category.objects.create(title='Category with no posts')

    def setUp(self):
        self.post = Post.objects.create(
            author=self.author,
            category=self.category,
            title='Test Post',
            text='Test content'
        )
        with freeze_time(datetime.now() + timedelta(seconds=1)):
            self.another_post = Post.objects.create(
                author=self.another_author,
                category=self.category,
                title='Test Post from another user',
                text='Test content'
            )
        self.client.force_authenticate(user=self.blogger)

    def test_list_posts(self):
        response = self.client.get(reverse('api:post-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(response.data['results'][0]['my_favorite'], False)
        self.assertEqual(response.data['results'][0]['my_vote'], 0)

    def test_create_post(self):
        data = {
            'title': 'New Post',
            'text': 'New content',
            'category': self.category
        }
        response = self.client.post(reverse('api:post-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 3)

    def test_non_blogger_user_cannot_create_post(self):
        self.client.force_authenticate(user=self.non_blogger_user)
        response = self.client.get(reverse('api:post-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = {
            'title': 'New Post',
            'text': 'New content',
            'category': self.category
        }
        response = self.client.post(reverse('api:post-list'), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_user_cannot_create_post(self):
        self.client.logout()
        response = self.client.get(reverse('api:post-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = {
            'title': 'New Post',
            'text': 'New content',
            'category': self.category
        }
        response = self.client.post(reverse('api:post-list'), data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_post(self):
        url = reverse('api:post-detail', kwargs={'pk': self.post.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Post')

    def test_update_post(self):
        url = reverse('api:post-detail', kwargs={'pk': self.post.pk})
        data = {
            'title': 'Updated Post',
            'text': 'Updated content',
            'category': self.category,
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Updated Post')

    def test_partial_update_post(self):
        url = reverse('api:post-detail', kwargs={'pk': self.post.pk})
        data = {
            'title': 'Partially Updated Post'
        }
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Partially Updated Post')

    def test_non_author_cannot_update_post(self):
        self.client.force_authenticate(user=self.another_blogger)

        url = reverse('api:post-detail', kwargs={'pk': self.post.pk})
        data = {'title': 'Another blogger user update'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_post(self):
        url = reverse('api:post-detail', kwargs={'pk': self.post.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Post.objects.count(), 1)  # was 2

    def test_non_author_cannot_delete_post(self):
        self.client.force_authenticate(user=self.another_blogger)
        url = reverse('api:post-detail', kwargs={'pk': self.post.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Post.objects.count(), 2)

    def test_posts_by_author(self):
        url = reverse('api:post-author-posts', kwargs={'user_id': self.blogger.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)

    def test_post_filtering(self):
        response = self.client.get(reverse('api:post-list'), {'category': self.category.title})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

        response = self.client.get(reverse('api:post-list'), {'category': self.empty_category.title})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

    def test_post_ordering(self):
        response = self.client.get(reverse('api:post-list'), {'ordering': '-created_at'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['title'], 'Test Post from another user')

        response = self.client.get(reverse('api:post-list'), {'ordering': 'created_at'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['title'], 'Test Post')


class CommentViewSetTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.blogger = User.objects.create_user(username='testuser', password='testpass', email='em@il.com')
        cls.another_blogger = User.objects.create_user(username='testuser2', password='testpass', email='em@aail.com')
        cls.staff_user = User.objects.create_user(username='testuser3', password='testpass', email='email@email.ml',
                                                  is_staff=True)
        bloggers = Group.objects.create(name='Bloggers')
        cls.blogger.groups.add(bloggers)
        cls.another_blogger.groups.add(bloggers)
        cls.author = Author.objects.get(user=cls.blogger)
        cls.another_author = Author.objects.get(user=cls.another_blogger)
        cls.category = Category.objects.create(title='Test Category')
        cls.post = Post.objects.create(
            author=cls.author,
            category=cls.category,
            title='Test Post',
            text='Test content'
        )

    def setUp(self):
        self.comment = Comment.objects.create(
            author=self.blogger,
            post=self.post,
            text='Test comment'
        )
        self.client.force_authenticate(user=self.blogger)

    def test_list_comments(self):
        url = reverse('api:comment-list', kwargs={'post_id': self.post.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_retrieve_comment(self):
        url = reverse('api:comment-detail', kwargs={'post_id': self.post.id, 'comment_id': self.comment.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['text'], 'Test comment')

    def test_create_comment(self):
        url = reverse('api:comment-list', kwargs={'post_id': self.post.id})
        data = {'text': 'New comment'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 2)

    def test_update_comment(self):
        url = reverse('api:comment-detail', kwargs={'post_id': self.post.id, 'comment_id': self.comment.id})
        data = {'text': 'Updated comment'}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.text, 'Updated comment')

    def test_partial_update_comment(self):
        url = reverse('api:comment-detail', kwargs={'post_id': self.post.id, 'comment_id': self.comment.id})
        data = {'text': 'Partially updated comment'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.text, 'Partially updated comment')

    def test_delete_comment(self):
        url = reverse('api:comment-detail', kwargs={'post_id': self.post.id, 'comment_id': self.comment.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Comment.objects.count(), 0)

    def test_list_comments_ordering(self):
        with freeze_time(datetime.now() + timedelta(seconds=1)):
            Comment.objects.create(author=self.blogger, post=self.post, text='Second comment')
        url = reverse('api:comment-list', kwargs={'post_id': self.post.id})
        response = self.client.get(url + '?ordering=-created_at')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['text'], 'Second comment')

    def test_filter_my_comments(self):
        Comment.objects.create(author=self.another_blogger, post=self.post, text='Another user comment')
        url = reverse('api:comment-list', kwargs={'post_id': self.post.id})
        response = self.client.get(url + '?is_my_comment=true')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['text'], 'Test comment')

    def test_comment_not_found(self):
        url = reverse('api:comment-detail', kwargs={'post_id': self.post.id, 'comment_id': 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthorized_user_cannot_create_comment(self):
        self.client.logout()
        url = reverse('api:comment-list', kwargs={'post_id': self.post.id})
        data = {'text': 'Unauthorized comment'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_cannot_update_others_comment(self):
        self.client.force_authenticate(user=self.another_blogger)
        url = reverse('api:comment-detail', kwargs={'post_id': self.post.id, 'comment_id': self.comment.id})
        data = {'text': 'Trying to update'}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_delete_any_comment(self):
        self.client.force_authenticate(user=self.staff_user)
        url = reverse('api:comment-detail', kwargs={'post_id': self.post.id, 'comment_id': self.comment.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_pagination(self):
        for i in range(15):
            Comment.objects.create(author=self.blogger, post=self.post, text=f'Comment {i}')
        url = reverse('api:comment-list', kwargs={'post_id': self.post.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('next', response.data)
        self.assertIsNotNone(response.data['next'])
