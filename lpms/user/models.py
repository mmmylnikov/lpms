
from allauth.socialaccount.models import SocialAccount
from django.db import models
from django.db.models import QuerySet
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group as AbstractGroup
from django.urls import reverse_lazy

from user.utils import GithubApi


class Pull(models.Model):
    repo = models.ForeignKey('Repo', on_delete=models.PROTECT,
                             verbose_name='Репозиторий')
    number = models.SmallIntegerField(verbose_name='Номер')
    title = models.CharField(max_length=1024, verbose_name='Название')
    url = models.CharField(max_length=1024, verbose_name='URL')
    html_url = models.CharField(max_length=1024, verbose_name='HTML URL')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлен')

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name = 'Пулл-реквест'
        verbose_name_plural = 'Пулл-реквесты'
        ordering = ('-created_at', )
        get_latest_by = 'created_at'


class Repo(models.Model):
    user = models.ForeignKey('User', on_delete=models.PROTECT,
                             verbose_name='Пользователь')
    name = models.CharField(max_length=512, verbose_name='Имя')
    full_name = models.CharField(max_length=512, verbose_name='Полное имя')
    url = models.CharField(max_length=1024, verbose_name='URL')
    html_url = models.CharField(max_length=1024, verbose_name='HTML URL')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлен')

    def __str__(self) -> str:
        return self.full_name

    def update_pulls(self) -> QuerySet[Pull]:
        pulls = GithubApi().get_pulls_from_repo(self.full_name)
        for pull in pulls:
            repo_pull, created = Pull.objects.get_or_create(
                repo=self, number=pull.number, title=pull.title,
                url=pull.url, html_url=pull.html_url)
        return Pull.objects.filter(repo=self)

    class Meta:
        verbose_name = 'Репозиторий'
        verbose_name_plural = 'Репозитории'
        ordering = ('-created_at', )
        get_latest_by = 'created_at'


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
    notify = models.BooleanField(
        default=False,
        verbose_name='Присылать уведомления')
    is_tutor = models.BooleanField(
        default=False,
        verbose_name='Куратор',
    )
    is_admin = models.BooleanField(
        default=False,
        verbose_name='Администратор',
    )

    @property
    def notify_icon(self) -> str:
        if self.notify:
            return 'bi bi-bell-fill'
        return 'bi bi-bell-slash-fill'

    @property
    def github_account(self) -> SocialAccount | None:
        accounts = {}  # type: ignore
        for account in self.socialaccount_set.all(  # type: ignore
                ).iterator():
            providers = accounts.setdefault(account.provider, [])
            providers.append(account)
        if accounts.get('github'):
            return accounts['github'][0]
        else:
            return None

    @property
    def full_name(self) -> str:
        return f'{self.last_name} {self.first_name}'
    full_name.fget.short_description = 'ФИО'  # type: ignore

    @property
    def github_url(self) -> str | None:
        if not self.gh_username:
            return None
        return f'https://github.com/{self.gh_username}'

    @property
    def tg_url(self) -> str | None:
        if not self.tg_username:
            return None
        return f'https://t.me/{self.tg_username}'

    @property
    def email_url(self) -> str | None:
        if not self.email:
            return None
        return f'mailto:{self.email}'

    # @property
    # def is_tutor(self) -> bool:
    #     if self.groups.filter(pk=GroupEnum.GROUP_TUTOR_ID.value).count() > 0:
    #         return True
    #     return False

    def switch_notify(self) -> bool:
        self.notify = not self.notify
        self.save()
        return self.notify

    def update_repos(self) -> QuerySet[Repo]:
        repos = GithubApi().get_repos_from_user(self.username)
        for repo in repos:
            user_repo, created = Repo.objects.get_or_create(
                user=self, name=repo.name, full_name=repo.full_name,
                url=repo.url, html_url=repo.html_url)
        return Repo.objects.filter(user=self)

    def __str__(self) -> str:
        if not self.last_name and not self.first_name:
            output = self.username
        else:
            output = f'{self.last_name} {self.first_name}'
        if self.is_tutor:
            return f'{output} (куратор)'
        return output

    def get_absolute_url(self) -> str:
        return reverse_lazy("user_detail_view", kwargs={'slug': self.username})

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-is_superuser', '-is_admin', '-is_tutor', '-is_active',
                    'last_name', 'first_name', 'username']
