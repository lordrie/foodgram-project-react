from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class User(AbstractUser):
    """Кастомная модель пользователя."""
    username = models.CharField(
        'Username', max_length=149, unique=True,
        validators=[RegexValidator(regex=r'^[\w.@+-]+\Z')])
    first_name = models.CharField('Имя', max_length=150)
    last_name = models.CharField('Фамилия', max_length=150)
    email = models.EmailField('email', max_length=254, unique=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.username}, {self.email}'


class Subscription(models.Model):
    """Модель подписок."""
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='subscriptions')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='followers')
    created = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [models.UniqueConstraint(
            fields=('user', 'author'), name='unique_subscription')]

    def __str__(self):
        return f'{self.user} подписался на {self.author}'
