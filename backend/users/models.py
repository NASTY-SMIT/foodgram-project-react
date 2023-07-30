from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import validate_email
from django.db import models


class User(AbstractUser):

    email = models.EmailField(
        verbose_name='Почта',
        max_length=254,
        unique=True,
        help_text='Required. 254 characters or fewer.',
        validators=[validate_email],
        error_messages={
            'unique': "A user with that email already exists.",
        },
    )
    username = models.CharField(
        verbose_name='Юзернейм',
        max_length=150,
        unique=True,
        help_text=('Required. 150 characters or fewer. Letters, '
                   'digits and @/./+/-/_ only.'),
        validators=[UnicodeUsernameValidator()],
        error_messages={
            'unique': "A user with that username already exists.",
        },
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=128,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ("username",)

    def __str__(self) -> str:
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="follower",
        verbose_name='Подписчик')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following",
        verbose_name='Автор')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"],
                name="unique_follow",
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='check_not_self_follow'
            ),
        ]
