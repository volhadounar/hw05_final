from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

User = get_user_model()


class Group(models.Model):
    title = models.CharField('Имя', max_length=200, help_text='Введите имя группы.\
                            Максимум 200 симоволов.')
    slug = models.SlugField('Адрес', max_length=50, unique=True,
                            help_text='Введите адрес группы.\
                            Максимум 50 симоволов.')
    description = models.TextField('Описание', help_text='Введите описание')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'


class Post(models.Model):
    text = models.TextField('Текст', help_text='Введите текст', db_index=True)
    pub_date = models.DateTimeField('Дата публикации',
                                    auto_now_add=True,
                                    help_text='Введите дату публикации')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='posts', null=False,
                               db_index=True, help_text='Автор поста')
    group = models.ForeignKey(Group, on_delete=models.SET_NULL,
                              blank=True, null=True, related_name='posts',
                              db_index=True, help_text='Группа')
    image = models.ImageField('Иллюстрация', upload_to='posts/', blank=True,
                              null=True,
                              help_text='Загрузите иллюстацию к статье')

    def get_absolute_url(self):
        return reverse('post', kwargs={'username': self.author.username,
                       'post_id': self.id})

    def __str__(self):
        return self.text

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'


class Comment(models.Model):
    text = models.TextField('Текст', help_text='Введите текст')
    created = models.DateTimeField('Дата создания', auto_now_add=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name='comments', null=False,
                             db_index=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='comments', null=False,
                               db_index=True)


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='follower', null=False,
                             db_index=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='following', null=False,
                               db_index=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'],
                                    name='unique_follow'),
        ]
