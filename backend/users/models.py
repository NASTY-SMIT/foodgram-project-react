from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


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
