from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse
from freezegun import freeze_time

from blog.models import Author, Post, Category, Comment
from rating.models import PostRating

User = get_user_model()


# Only users in the Bloggers group can create posts, as post creation requires an entry in the
# Authors table. This entry is automatically created (by the "create_or_delete_blog_author" signal)
# when a user is assigned to the Blogger group. Readers cannot create posts because they lack
# an entry in the Authors table.
# Thus, you can create an instance of the Author model by yourself, or by assigning the user to the Bloggers group

class PostListViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK', email='em@il.com')
        cls.author = Author.objects.create(user=cls.user, bio='Biography.')
        cls.category = Category.objects.create(title='BlogCategory.')
        cls.another_category = Category.objects.create(title='AnotherCategory')
        cls.post1 = Post.objects.create(author=cls.author, category=cls.category, title='Title1', text='...')
        with freeze_time(datetime.now() + timedelta(seconds=1)):
            cls.post2 = Post.objects.create(author=cls.author, category=cls.another_category, title='Title2', text='...')

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/blog/all/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('blog:posts'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('blog:posts'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post_list.html')

    def test_pagination_is_5(self):
        for _ in range(6):
            Post.objects.create(author=self.author, category=self.category, title='Title', text='...')
        response = self.client.get(reverse('blog:posts'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['is_paginated'])
        self.assertEqual(len(response.context['post_list']), 5)

    def test_filtering_by_category(self):
        response = self.client.get(reverse('blog:posts'), {'category': self.category.title})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['post_list']), 1)
        self.assertEqual(response.context['post_list'][0].category, self.category)

        response = self.client.get(reverse('blog:posts'), {'category': self.another_category.title})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['post_list']), 1)
        self.assertEqual(response.context['post_list'][0].category, self.another_category)

    def test_ordering_by_rating(self):
        # When a post is created, a rating of 0 is automatically assigned to the author.
        PostRating.objects.filter(owner=self.user, obj=self.post1).update(vote=1)
        PostRating.objects.filter(owner=self.user, obj=self.post2).update(vote=-1)

        response = self.client.get(reverse('blog:posts'), {'ordering': 'rating'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['post_list'][0], self.post2)
        self.assertEqual(response.context['post_list'][1], self.post1)

        response = self.client.get(reverse('blog:posts'), {'ordering': '-rating'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['post_list'][0], self.post1)
        self.assertEqual(response.context['post_list'][1], self.post2)

    def test_ordering_by_created_at(self):
        response = self.client.get(reverse('blog:posts'), {'ordering': 'created_at'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['post_list'][0], self.post1)
        self.assertEqual(response.context['post_list'][1], self.post2)

        response = self.client.get(reverse('blog:posts'), {'ordering': '-created_at'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['post_list'][0], self.post2)
        self.assertEqual(response.context['post_list'][1], self.post1)


class PostDetailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK', email='em@il.com')
        cls.author = Author.objects.create(user=cls.user, bio='Biography.')
        cls.category = Category.objects.create(title='BlogCategory.')
        cls.post = Post.objects.create(author=cls.author, category=cls.category, title='Title', text='...')

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(f'/blog/{self.post.pk}/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('blog:post-detail', args=(self.post.pk,)))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('blog:post-detail', args=(self.post.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post_detail.html')

    def test_post_root_comment_pagination_is_5(self):
        for i in range(1, 7):
            # root comments
            Comment.objects.create(post=self.post, author=self.user, text='...', reply_to=None)
            # replies
            Comment.objects.create(post=self.post, author=self.user, text='...', reply_to=Comment.objects.get(pk=i))

        response = self.client.get(reverse('blog:post-detail', args=(self.post.pk,)))
        self.assertEqual(len(response.context['page_obj']), 5)


class CreatePostViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Let's create Author instance by assigning the user to the Bloggers group
        bloggers = Group.objects.create(name='Bloggers')
        readers = Group.objects.create(name='Readers')
        cls.blogger = User.objects.create_user(username='blogger', password='1X<ISRUkw+tuK', email='em@il.com')
        cls.blogger.groups.add(bloggers)
        cls.reader = User.objects.create_user(username='reader', password='2HJ1vRV0Z&3iD', email='em@ail.com')
        cls.reader.groups.add(readers)
        cls.category = Category.objects.create(title='BlogCategory')

    def setUp(self):
        self.client.force_login(self.blogger)

    def test_create_post_view_url_exists_at_desired_location(self):
        response = self.client.get('/blog/create/')
        self.assertEqual(response.status_code, 200)

    def test_create_post_view_url_accessible_by_name(self):
        response = self.client.get(reverse('blog:create-post'))
        self.assertEqual(response.status_code, 200)

    def test_create_post_view_uses_correct_template(self):
        response = self.client.get(reverse('blog:create-post'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post_form.html')

    def test_create_post_by_blogger_user_success(self):
        response = self.client.post(reverse('blog:create-post'), {
            'title': 'New Post by Blogger',
            'category': self.category.pk,
            'text': 'Some content'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Post.objects.filter(title='New Post by Blogger').exists())

    def test_create_post_by_reader_user_fails(self):
        self.client.logout()
        self.client.force_login(self.reader)
        response = self.client.get(reverse('blog:create-post'))
        self.assertEqual(response.status_code, 403)

    def test_guest_user_redirects_to_login_page(self):
        self.client.logout()
        response = self.client.get(reverse('blog:create-post'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/blog/create/')


class EditPostViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK', email='em@il.com')
        cls.other_user = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD',
                                                  email='em@ail.com')
        cls.admin_user = User.objects.create_superuser(username='admin', password='adminpass',
                                                       email='admin@example.com')
        cls.author = Author.objects.create(user=cls.user, bio='Biography')
        cls.other_author = Author.objects.create(user=cls.other_user, bio='Other Biography')
        cls.category = Category.objects.create(title='BlogCategory')
        cls.post = Post.objects.create(author=cls.author, category=cls.category, title='Original Post', text='...')

    def setUp(self):
        self.client.force_login(self.user)

    def test_edit_post_view_url_exists_at_desired_location(self):
        response = self.client.get(f'/blog/{self.post.pk}/edit/')
        self.assertEqual(response.status_code, 200)

    def test_edit_post_view_url_accessible_by_name(self):
        response = self.client.get(reverse('blog:edit-post', args=(self.post.pk,)))
        self.assertEqual(response.status_code, 200)

    def test_edit_post_view_uses_correct_template(self):
        response = self.client.get(reverse('blog:edit-post', args=(self.post.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post_form.html')

    def test_edit_post_success(self):
        response = self.client.post(reverse('blog:edit-post', args=(self.post.pk,)), {
            'title': 'Updated Post',
            'category': self.category.pk,
            'text': 'Updated content'
        })
        self.assertEqual(response.status_code, 302)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Updated Post')
        self.assertEqual(self.post.text, 'Updated content')

    def test_edit_post_by_non_author(self):
        self.client.logout()
        self.client.force_login(self.other_user)
        response = self.client.get(reverse('blog:edit-post', args=(self.post.pk,)))
        self.assertEqual(response.status_code, 403)

    def test_edit_post_by_admin(self):
        self.client.logout()
        self.client.force_login(self.admin_user)
        response = self.client.post(reverse('blog:edit-post', args=(self.post.pk,)), {
            'title': 'Admin Updated Post',
            'category': self.category.pk,
            'text': 'Admin updated content'
        })
        self.assertEqual(response.status_code, 302)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Admin Updated Post')
        self.assertEqual(self.post.text, 'Admin updated content')

    def test_guest_user_redirects_to_login_page(self):
        self.client.logout()
        response = self.client.post(reverse('blog:edit-post', args=(self.post.pk,)), {
            'title': 'Admin Updated Post',
            'category': self.category.pk,
            'text': 'Admin updated content'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/accounts/login/?next=/blog/{self.post.pk}/edit/')


class DeletePostViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK', email='em@il.com')
        cls.other_user = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD',
                                                  email='other@user.com')
        cls.admin_user = User.objects.create_superuser(username='admin', password='adminpass',
                                                       email='admin@example.com')
        cls.author = Author.objects.create(user=cls.user, bio='Biography')
        cls.other_author = Author.objects.create(user=cls.other_user, bio='Other Biography')
        cls.category = Category.objects.create(title='BlogCategory')
        cls.post = Post.objects.create(author=cls.author, category=cls.category, title='Post to Delete', text='...')

    def setUp(self):
        self.client.force_login(self.user)

    def test_delete_post_view_url_exists_at_desired_location(self):
        response = self.client.get(f'/blog/{self.post.pk}/delete/')
        self.assertEqual(response.status_code, 200)

    def test_delete_post_view_url_accessible_by_name(self):
        response = self.client.get(reverse('blog:delete-post', args=(self.post.pk,)))
        self.assertEqual(response.status_code, 200)

    def test_delete_post_view_uses_correct_template(self):
        response = self.client.get(reverse('blog:delete-post', args=(self.post.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post_confirm_delete.html')

    def test_delete_post_success(self):
        response = self.client.post(reverse('blog:delete-post', args=(self.post.pk,)), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Post.objects.filter(pk=self.post.pk).exists())

    def test_delete_post_by_non_author(self):
        self.client.logout()
        self.client.force_login(self.other_user)
        response = self.client.post(reverse('blog:delete-post', args=(self.post.pk,)))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Post.objects.filter(pk=self.post.pk).exists())

    def test_delete_post_by_admin(self):
        self.client.logout()
        self.client.force_login(self.admin_user)
        response = self.client.post(reverse('blog:delete-post', args=(self.post.pk,)), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Post.objects.filter(pk=self.post.pk).exists())

    def test_guest_user_redirects_to_login_page(self):
        self.client.logout()
        response = self.client.post(reverse('blog:delete-post', args=(self.post.pk,)))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/accounts/login/?next=/blog/{self.post.pk}/delete/')


class CommentCreateViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK', email='em@il.com')
        cls.author = Author.objects.create(user=cls.user, bio='Biography.')
        cls.category = Category.objects.create(title='BlogCategory')
        cls.post = Post.objects.create(author=cls.author, category=cls.category, title='Title', text='Post text')

    def setUp(self):
        self.client.force_login(self.user)

    def test_create_comment_uses_correct_template(self):
        url = reverse('blog:create-comment', kwargs={'post_pk': self.post.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/comment_form.html')

    def test_create_comment(self):
        url = reverse('blog:create-comment', kwargs={'post_pk': self.post.pk})
        response = self.client.post(url, {'text': 'This is a comment'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Comment.objects.filter(text='This is a comment', post=self.post, author=self.user).exists())

    def test_create_reply(self):
        parent_comment = Comment.objects.create(post=self.post, author=self.user, text='Parent comment')
        url = reverse('blog:reply-comment', kwargs={'post_pk': self.post.pk, 'comment_pk': parent_comment.pk})
        response = self.client.post(url, {'text': 'This is a reply comment'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Comment.objects.filter(text='This is a reply comment', post=self.post, reply_to=parent_comment,
                                               author=self.user).exists())

    def test_guest_user_redirects_to_login_page(self):
        self.client.logout()
        response = self.client.post(reverse('blog:create-comment', kwargs={'post_pk': self.post.pk}),
                                    {'text': 'This is a comment'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/accounts/login/?next=/blog/{self.post.pk}/post-comment/')


class CommentEditViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK', email='em@il.com')
        cls.user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD', email='user2@em.com')
        cls.author = Author.objects.create(user=cls.user, bio='Biography.')
        cls.category = Category.objects.create(title='BlogCategory')
        cls.post = Post.objects.create(author=cls.author, category=cls.category, title='Title', text='Post text')
        cls.comment = Comment.objects.create(post=cls.post, author=cls.user, text='Original comment')

    def setUp(self):
        self.client.force_login(self.user)

    def test_edit_comment_uses_correct_template(self):
        url = reverse('blog:edit-comment', kwargs={'post_pk': self.post.pk, 'comment_pk': self.comment.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/comment_form.html')

    def test_edit_comment(self):
        url = reverse('blog:edit-comment', kwargs={'post_pk': self.post.pk, 'comment_pk': self.comment.pk})
        response = self.client.post(url, {'text': 'Updated comment'})
        self.assertEqual(response.status_code, 302)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.text, 'Updated comment')

    def test_edit_comment_permission_denied(self):
        self.client.logout()
        self.client.force_login(self.user2)
        url = reverse('blog:edit-comment', kwargs={'post_pk': self.post.pk, 'comment_pk': self.comment.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_guest_user_redirects_to_login_page(self):
        self.client.logout()
        response = self.client.post(
            reverse('blog:edit-comment', kwargs={'post_pk': self.post.pk, 'comment_pk': self.comment.pk}),
            {'text': 'Updated comment'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/accounts/login/?next=/blog/{self.post.pk}/edit-comment/{self.comment.pk}/')


class CommentDeleteViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK', email='em@il.com')
        cls.user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD', email='user2@em.com')
        cls.author = Author.objects.create(user=cls.user, bio='Biography.')
        cls.category = Category.objects.create(title='BlogCategory')
        cls.post = Post.objects.create(author=cls.author, category=cls.category, title='Title', text='Post text')
        cls.comment = Comment.objects.create(post=cls.post, author=cls.user, text='Comment to be deleted')

    def setUp(self):
        self.client.force_login(self.user)

    def test_delete_uses_correct_template(self):
        url = reverse('blog:delete-comment', kwargs={'post_pk': self.post.pk, 'comment_pk': self.comment.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/comment_confirm_delete.html')

    def test_delete_comment(self):
        url = reverse('blog:delete-comment', kwargs={'post_pk': self.post.pk, 'comment_pk': self.comment.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Comment.objects.filter(pk=self.comment.pk).exists())

    def test_delete_comment_permission_denied(self):
        self.client.logout()
        self.client.force_login(self.user2)
        url = reverse('blog:delete-comment', kwargs={'post_pk': self.post.pk, 'comment_pk': self.comment.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_guest_user_redirects_to_login_page(self):
        self.client.logout()
        response = self.client.post(
            reverse('blog:delete-comment', kwargs={'post_pk': self.post.pk, 'comment_pk': self.comment.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/accounts/login/?next=/blog/{self.post.pk}/delete-comment/{self.comment.pk}/')
