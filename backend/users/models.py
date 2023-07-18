from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.validators import validate_email
from django.db import models
from .managers import UserManager


class User(AbstractUser):
    username = models.CharField(
        verbose_name="username",
        max_length=150,
        unique=True,
        help_text=('Required. 150 characters or fewer. Letters, '
                   'digits and @/./+/-/_ only.'),
        validators=[UnicodeUsernameValidator()],
        error_messages={
            'unique': "A user with that username already exists.",
        },
    )
    password = models.CharField(verbose_name="Пароль",  max_length=150)
    email = models.CharField(
        max_length=254,
        unique=True,
        help_text='Required. 254 characters or fewer.',
        validators=[validate_email],
        error_messages={
            'unique': "A user with that email already exists.",
        },
    )
    first_name = models.CharField(verbose_name="Имя",
                                  max_length=150, blank=True)
    last_name = models.CharField(verbose_name="Фамилия",
                                 max_length=150, blank=True)
    superuser = models.BooleanField('Админ', default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    objects = UserManager()

    class Meta:
        verbose_name = "Пользователь"
        ordering = ("username",)

    def __str__(self):
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
