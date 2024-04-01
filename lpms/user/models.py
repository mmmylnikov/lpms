from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group as AbstractGroup
from django.urls import reverse_lazy

from user.enums import GroupEnum


class Group(AbstractGroup):
    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'


class User(AbstractUser):
    gh_username = models.CharField(
        max_length=64,
        null=True,
        verbose_name='GitHub')
    tg_username = models.CharField(
        max_length=64,
        null=True,
        verbose_name='Telegram')
    groups = models.ManyToManyField(
        Group,
        verbose_name='Роли',
        blank=True,
        help_text=(
            'Группы, к которым принадлежит этот пользователь. '
            'Пользователь получит все разрешения '
            'предоставленные каждой из его групп.'
        ),
        related_name="user_set",
        related_query_name="user",
    )

    def __str__(self) -> str:
        output = f'{self.last_name} {self.first_name}'
        if self.groups.filter(pk=GroupEnum.GROUP_TUTOR_ID.value).count() > 0:
            return f'{output} (куратор)'
        return output

    def get_absolute_url(self) -> str:
        return reverse_lazy("user_detail_view", kwargs={'slug': self.username})
