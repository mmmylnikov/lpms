from django.db import models

from user.models import User
from notify.enums import Providers, MessageStatuses


class Provider(models.Model):
    name_choices = ((provider.value, provider.name) for provider in Providers)
    name = models.CharField(max_length=64,
                            choices=name_choices, verbose_name='Название',
                            unique=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлен')

    def __str__(self) -> str:
        return f'{self.name}'

    class Meta:
        verbose_name = 'Провайдер'
        verbose_name_plural = 'Провайдеры'
        ordering = ('-created_at', )
        get_latest_by = 'created_at'


class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT,
                             verbose_name='Пользователь')
    provider = models.ForeignKey(Provider, on_delete=models.PROTECT,
                                 verbose_name='Провайдер')
    chat_uid = models.CharField(max_length=256, verbose_name='ID канала')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлен')

    def __str__(self) -> str:
        return f'{self.chat_uid}'

    class Meta:
        verbose_name = 'Аккаунт'
        verbose_name_plural = 'Аккаунты'
        ordering = ('-created_at', )
        get_latest_by = 'created_at'


class Status(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT,
                             verbose_name='Пользователь')
    account = models.ForeignKey(Account, on_delete=models.PROTECT,
                                verbose_name='Аккаунт')
    enabled = models.BooleanField(default=False, verbose_name='Включены?')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлен')

    def __str__(self) -> str:
        return str(self.enabled)

    class Meta:
        verbose_name = 'Статус'
        verbose_name_plural = 'Статусы'
        ordering = ('-created_at', )
        get_latest_by = 'created_at'


class Message(models.Model):
    status_choices = (
        (status.value, status.name) for status in MessageStatuses)
    user = models.ForeignKey(User, on_delete=models.PROTECT,
                             verbose_name='Пользователь')
    account = models.ForeignKey(Account, on_delete=models.PROTECT,
                                verbose_name='Аккаунт')
    text = models.CharField(max_length=1024, verbose_name='Текст')
    status = models.CharField(max_length=10, choices=status_choices,
                              verbose_name='Статус')
    status_comment = models.CharField(max_length=256,
                                      verbose_name='Примечание',
                                      null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлен')

    def __str__(self) -> str:
        return f'{self.text}: {self.status}'

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ('-created_at', )
        get_latest_by = 'created_at'
