from django.test import TestCase, Client
from .models import Post, Group, Comment
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.conf import settings
from .forms import CommentForm
from time import sleep
from django.core.cache import cache

User = get_user_model()


class TestStringMethods(TestCase):
    def setUp(self):
        self.client = Client()
        self.client_with_unlogged = Client()
        self.sarah = User.objects.create_user(
            username='sarah', email='connor.s@skynet.com', password='12345')
        self.olga = User.objects.create_user(
            username='olga', email='olga.s@skynet.com', password='54321')
        self.rick = User.objects.create_user(
            username='rick', email='rick.s@skynet.com', password='12345')
        self.user_sarah = User.objects.get(username=self.sarah)
        self.user_olga = User.objects.get(username=self.olga)
        self.user_rick = User.objects.get(username=self.rick)
        self.client.force_login(self.user_sarah)
        self.group = Group.objects.create(title='Grupo de prueba',
                                          slug='prueba',
                                          description='Mucho gusto')

    def test_if_register(self):
        response = self.client.post(f'/{self.sarah}/')
        self.assertEqual(response.status_code, 200)

    def check_param(self, url, args, user, my_text):
        post = get_object_or_404(Post, text=my_text)
        self.assertEqual(post.author, user)
        self.assertEqual(post.group, self.group)
        response = self.client.get(url, kwargs_view=args)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, my_text)

    def test_if_logged_user_can_create_post(self):
        url_new = reverse('new_post')
        old_user_objcnt = self.user_sarah.posts.count()
        my_text = '¡Qué mala suerte!'
        response = self.client.post(url_new, {'text': my_text,
                                    'group': self.group.id}, follow=True)
        self.assertEqual(response.status_code, 200)
        new_cnt = Post.objects.filter(author=self.user_sarah).count()
        self.assertNotEqual(old_user_objcnt, new_cnt)
        final_url = reverse('index')
        cache.clear()
        self.check_param(final_url, '', self.user_sarah, my_text)

    def test_if_not_logged_user_can_create_post(self):
        url_new = reverse('new_post')
        old_post_cnt = Post.objects.filter(author=self.sarah).count()
        my_text = '¡Qué faena!'
        response = self.client_with_unlogged.post(url_new,
                                                  {'text': my_text,
                                                   'group': self.group.id,
                                                   'author': self.sarah},
                                                  follow=True)
        self.assertEqual(response.status_code, 200)
        new_post_cnt = Post.objects.filter(author=self.sarah).count()
        self.assertEqual(old_post_cnt, new_post_cnt)
        self.assertRedirects(response, '%s?next=%s' %
                             (settings.LOGIN_URL, url_new))

    def get_dict_of_urls(self, user, my_text):
        post = get_object_or_404(Post, text=my_text, author=user)
        url_main = reverse('index')
        kwargs_edit = {'username': user.username, 'post_id': post.id}
        url_edit = reverse('post_edit', kwargs=kwargs_edit)
        kwargs_view = {'username': user.username, 'post_id': post.id}
        url_view = reverse('post', kwargs=kwargs_view)
        return {url_main: '', url_view: kwargs_view, url_edit: kwargs_edit}

    def get_list_of_urls_for_img(self, user, my_text, gr_slug):
        post = get_object_or_404(Post, text=my_text, author=user)
        url_main = reverse('index')
        url_gr = reverse('group_posts', kwargs={'slug': gr_slug})
        url_view = reverse('post', kwargs={'username': user.username,
                           'post_id': post.id})
        return [url_main, url_view, url_gr]

    def test_if_create_post(self):
        old_user_objcnt = self.user_sarah.posts.count()
        new_text = 'Mi nueva nota.'
        url = reverse('new_post')
        response = self.client.post(url, {'text': new_text,
                                          'group': self.group.id},
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        new_cnt = Post.objects.filter(author=self.user_sarah).count()
        self.assertNotEqual(old_user_objcnt, new_cnt)
        dict_to_check = self.get_dict_of_urls(self.user_sarah, new_text)
        cache.clear()
        for url, args in dict_to_check.items():
            self.check_param(url, args, self.user_sarah, new_text)

    def test_if_result_editing_post(self):
        new_post = Post.objects.create(author=self.user_sarah,
                                       text='Это мой пост!')
        old_user_objcnt = self.user_sarah.posts.count()
        changed_text = '¡no te permito qué me hables así!'
        kwargs_edit = {'username': self.sarah, 'post_id': new_post.id}
        url_edit = reverse('post_edit', kwargs=kwargs_edit)
        r = self.client.post(url_edit, {'text': changed_text,
                                        'group': self.group.id},
                             follow=True)
        self.assertEqual(r.status_code, 200)
        new_cnt = Post.objects.filter(author=self.user_sarah).count()
        self.assertEqual(old_user_objcnt, new_cnt)
        dict_to_check = self.get_dict_of_urls(self.user_sarah, changed_text)
        cache.clear()
        for url, args in dict_to_check.items():
            self.check_param(url, args, self.user_sarah, changed_text)

    def test_fault_page_error_404(self):
        response = self.client.get('/unknown_page/')
        self.assertEqual(response.status_code, 404)

    def test_load_user_img_file(self):
        text = 'Text 001'
        new_post = Post.objects.create(author=self.user_sarah,
                                       text=text, group=self.group)
        my_kwargs = {'username': self.sarah, 'post_id': new_post.id}
        url_post_edit = reverse('post_edit', kwargs=my_kwargs)
        with open('posts/flamencodance_mc2018_2-3.jpg', 'rb') as img:
            response = self.client.post(url_post_edit, {'text': text,
                                        'image': img, 'group': self.group.id})
        list_to_check = self.get_list_of_urls_for_img(self.user_sarah,
                                                      text, self.group.slug)
        for url in list_to_check:
            response = self.client.get(url, {'username': self.sarah,
                                             'post_id': new_post.id})
            self.assertEquals(response.status_code, 200)
            self.assertContains(response, '<img')

    def test_load_user_non_img_file(self):
        with open('posts/non_img_file.mp3', 'rb') as img:
            response = self.client.post(reverse('new_post'),
                                        {'text': 'Text 002', 'image': img},
                                        follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        form = response.context['form']
        self.assertIn('image', form.errors)

    def test_creating_comments(self):
        new_post = Post.objects.create(author=self.user_sarah,
                                       text='Un artículo popular',
                                       group=self.group)
        es_genial = 'Es genial!'
        response = self.client.post(reverse('add_comment',
                                    kwargs={'username': self.sarah,
                                            'post_id': new_post.id}),
                                    {'text': es_genial}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        form = response.context['form']
        self.assertIsInstance(form, CommentForm)
        obj_comment = get_object_or_404(Comment, post=new_post.id)
        self.assertEqual(es_genial, obj_comment.text)
        response = self.client.get(reverse('post',
                                   kwargs={'username': self.sarah,
                                           'post_id': new_post.id}))
        self.assertContains(response, es_genial)

    def test_cash(self):
        Post.objects.create(author=self.user_sarah,
                            text='1!')
        response = self.client.get(reverse('index'))
        self.assertContains(response,  '1!')
        sleep(2)
        Post.objects.create(author=self.user_sarah,
                            text='2!')
        response = self.client.get(reverse('index'))
        self.assertNotContains(response,  '2!')
        cache.clear()
        response = self.client.get(reverse('index'))
        self.assertContains(response,  '2!')

    def test_follow(self):
        Post.objects.create(author=self.user_olga,
                            text='De Olga', group=self.group)
        Post.objects.create(author=self.user_rick,
                            text='De Rick', group=self.group)
        self.client.post(reverse('profile_follow',
                         kwargs={'username': self.user_olga.username}))
        self.client.post(reverse('profile_follow',
                         kwargs={'username': self.user_rick.username}))
        cnt_following = self.user_sarah.follower.count()
        cnt_follower = self.user_sarah.following.count()
        self.assertEqual(2, cnt_following)
        self.assertEqual(0, cnt_follower)
        self.client.post(reverse('profile_unfollow',
                         kwargs={'username': self.user_rick.username}))
        cnt_following = self.user_sarah.follower.count()
        self.assertEqual(1, cnt_following)
        response = self.client.get(reverse('follow_index'))
        self.assertContains(response, 'De Olga')
        self.assertNotContains(response, 'De Rick')

    def tearDown(self):
        self.client.logout()
