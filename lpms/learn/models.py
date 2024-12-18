from typing import Any

from django.db import models
from django.urls import reverse_lazy
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from markdown import markdown
from allauth.socialaccount.models import SocialAccount

from user.models import User
from course.models import Track, Course, Enrollment, Team
from learn.enums import HomeworkStatuses, PullRequestPolicies


def parse_pull_request_url(url: str) -> dict[str, Any]:
    if not url.startswith('https://github.com'):
        raise ValidationError(f'Неверный URL: {url}')
    url_items = url.split('/')
    output: dict[str, Any] = {}
    if len(url_items) >= 4:
        output['username'] = url_items[3]
    if len(url_items) >= 5:
        output['repo_name'] = url_items[4]
    if len(url_items) >= 7:
        output['pull_num'] = int(url_items[6])
    return output


class HomeworkRepoValidator(RegexValidator):
    regex = (r'https:\/\/github.com'
             r'\/[a-zA-Z0-9-_]*\/[a-zA-Z0-9-_]*'
             r'\/pull\/[1-9][0-9]*')
    message = ('URL пулл-реквеста должен иметь формат '
               '"https://github.com/<username>/<repo_name>/pull/<pull_num>"')
    code = "invalid_url"


class Lesson(models.Model):
    track = models.ForeignKey(Track, on_delete=models.PROTECT,
                              verbose_name='Трек')
    name = models.CharField(max_length=128, verbose_name='Название')
    content = models.TextField(verbose_name='Контент', null=True, blank=True)
    video = models.CharField(max_length=512, null=True, blank=True,
                             verbose_name='Видеоролик')
    slide = models.CharField(max_length=512, null=True, blank=True,
                             verbose_name='Слайд')
    repo = models.CharField(max_length=512, null=True, blank=True,
                            verbose_name='Репозиторий')
    url = models.CharField(max_length=512, null=True, blank=True,
                           verbose_name='Ссылка')
    order = models.PositiveSmallIntegerField(verbose_name='Порядок', default=0)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлен')

    @property
    def video_uid(self) -> str | None:
        if not self.video:
            return None
        return self.video.replace('https://www.youtube.com/watch?v=', '')

    @property
    def slide_embed_url(self) -> str | None:
        if not self.slide:
            return None
        return self.slide.replace('/pub?', '/embed?')

    @property
    def added(self) -> str:
        output = []
        if self.content:
            output.append('К')
        if self.video:
            output.append('В')
        if self.slide:
            output.append('C')
        if self.repo:
            output.append('Р')
        if self.url:
            output.append('Л')
        return ', '.join(output)

    def __str__(self) -> str:
        return f'{self.track} - {self.name} ({self.order})'

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'
        ordering = ('track', 'order', 'name', )
        get_latest_by = 'created_at'


class Challenge(models.Model):
    pr_choices = (
        (policy.value.name, policy.value.label)
        for policy in PullRequestPolicies
    )
    track = models.ForeignKey(Track, on_delete=models.PROTECT,
                              verbose_name='Трек')
    name = models.CharField(max_length=128, verbose_name='Название')
    content = models.TextField(verbose_name='Контент', null=True, blank=True)
    repo = models.CharField(max_length=512, null=True, blank=True,
                            verbose_name='Репозиторий')
    url = models.CharField(max_length=512, null=True, blank=True,
                           verbose_name='Ссылка')
    order = models.PositiveSmallIntegerField(verbose_name='Порядок', default=0)
    pull_request_policy = models.CharField(
        max_length=32,
        choices=pr_choices,
        default=PullRequestPolicies.own_repo.value.name,
        verbose_name="Политика пулл-реквестов",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлен')

    @property
    def content_markdown(self) -> str:
        content = self.content if self.content else ''
        return markdown(content)

    @property
    def added(self) -> str:
        output = []
        if self.content:
            output.append('К')
        if self.repo:
            output.append('Р')
        if self.url:
            output.append('Л')
        return ', '.join(output)

    def __str__(self) -> str:
        return f'{self.track} - {self.name} ({self.order})'

    class Meta:
        verbose_name = 'Задание'
        verbose_name_plural = 'Задания'
        ordering = ('track', 'order', 'name', )
        get_latest_by = 'created_at'


class Week(models.Model):
    course = models.ForeignKey(Course, on_delete=models.PROTECT,
                               verbose_name='Курс')
    number = models.PositiveSmallIntegerField(verbose_name='Номер')
    description = models.TextField(null=True, blank=True,
                                   verbose_name='Комментарий')
    lessons = models.ManyToManyField(Lesson, verbose_name='Уроки', blank=True)
    challenges = models.ManyToManyField(Challenge, verbose_name='Задания',
                                        blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлен')

    @property
    def description_markdown(self) -> str:
        if self.description:
            return markdown(self.description)
        return ''

    @property
    def added(self) -> str:
        output = []
        if self.lessons:
            output.append(f'У:{self.lessons.count()}')
        if self.challenges:
            output.append(f'З:{self.challenges.count()}')
        return ', '.join(output)

    def __str__(self) -> str:
        date_change = "_".join([
            self.created_at.strftime("%Y%m%d"),
            self.updated_at.strftime("%Y%m%d"),
        ])
        return f'{date_change} | {self.course.slug} #{self.number}'

    class Meta:
        verbose_name = 'Неделя'
        verbose_name_plural = 'Недели'
        ordering = ('course', 'number')
        get_latest_by = 'created_at'


class Homework(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT,
                             verbose_name='Пользователь')
    challenge = models.ForeignKey(Challenge, on_delete=models.PROTECT,
                                  verbose_name='Задание')
    comment = models.TextField(null=True, blank=True,
                               verbose_name='Комментарий')
    tutor_comment = models.TextField(null=True, blank=True,
                                     verbose_name='Комментарий куратора')
    repo = models.CharField(max_length=512, null=True, blank=True,
                            validators=[HomeworkRepoValidator()],
                            verbose_name='Репозиторий')
    week = models.ForeignKey(Week, on_delete=models.PROTECT,
                             verbose_name='Неделя')
    team = models.ForeignKey(Team, on_delete=models.PROTECT,
                             verbose_name='Группа')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлен')

    def __str__(self) -> str:
        return f'{self.challenge} ({self.user.get_full_name()})'

    def get_student_absolute_url(self) -> str:
        return reverse_lazy("student_task_view", kwargs={
            'week_number': self.week.number,
            'team_slug': self.team.slug,
            'challenge_id': self.challenge.pk,
            })

    def get_tutor_absolute_url(self) -> str:
        return reverse_lazy("tutor_review_view", kwargs={
            'week_number': self.week.number,
            'team_slug': self.team.slug,
            'challenge_id': self.challenge.pk,
            'username': self.user.username,
            })

    def pull_request_policy_validator(
        self, pr_url: str
    ) -> None | ValidationError:
        challenge = self.challenge
        pr_policy = PullRequestPolicies[challenge.pull_request_policy]

        if pr_policy == PullRequestPolicies.any_repo:
            return None
        if pr_policy == PullRequestPolicies.any_repo_except_task:
            if not challenge.repo:
                return None
            task_repo = parse_pull_request_url(challenge.repo)
            pr_repo = parse_pull_request_url(pr_url)
            if not task_repo.get('username'):
                return None
            if all([
                task_repo['username'] == pr_repo['username'],
            ]):
                bad_repo_path = pr_policy.value.url_pattern.format(
                    username=task_repo['username'],
                )
                msg = f'Разрешено использовать: "{pr_policy.value.label}".'
                msg += f'\nНельзя: {bad_repo_path}'
                return ValidationError(msg, code='invalid_url')
            return None
        if pr_policy == PullRequestPolicies.own_repo:
            pr_repo = parse_pull_request_url(pr_url)
            gh_user: SocialAccount = self.user.github_account
            gh_username = gh_user.extra_data['login']
            if gh_username != pr_repo['username']:
                good_repo_path = pr_policy.value.url_pattern.format(
                    username=gh_username,
                )
                msg = f'Разрешено использовать: "{pr_policy.value.label}".'
                msg += f'\nМожно: {good_repo_path}'
                return ValidationError(msg, code="invalid_url")
            return None

    class Meta:
        verbose_name = 'Работа'
        verbose_name_plural = 'Работы'
        ordering = ('-created_at', )
        get_latest_by = 'created_at'


class HomeworkStatus(models.Model):
    status_choices = (
        (status.value.name, status.value.label) for status in HomeworkStatuses
    )
    student = models.ForeignKey(User, on_delete=models.PROTECT,
                                related_name='student_set',
                                verbose_name='Студент')
    tutor = models.ForeignKey(User, on_delete=models.PROTECT,
                              related_name='tutor_set',
                              verbose_name='Куратор')
    homework = models.ForeignKey(Homework, on_delete=models.PROTECT,
                                 verbose_name='Таск/Ревью')
    status = models.CharField(max_length=11, choices=status_choices,
                              default='available',
                              verbose_name='Статус')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлен')

    def __str__(self) -> str:
        return self.status_label

    @property
    def status_icon(self) -> str:
        return HomeworkStatuses[self.status].value.icon

    @property
    def status_label(self) -> str:
        return HomeworkStatuses[self.status].value.label

    @property
    def status_color(self) -> str:
        return HomeworkStatuses[self.status].value.color

    class Meta:
        verbose_name = 'Статус работы'
        verbose_name_plural = 'Статусы работ'
        ordering = ('tutor', 'student', '-updated_at', )
        get_latest_by = 'created_at'


class Program(models.Model):
    name = models.CharField(max_length=256, verbose_name='Название')
    description = models.TextField(null=True, blank=True,
                                   verbose_name='Описание')
    course = models.ForeignKey(Course, on_delete=models.PROTECT,
                               verbose_name='Курс')
    weeks = models.ManyToManyField(Week, verbose_name='Недели')
    enrollments = models.ManyToManyField(Enrollment, verbose_name='Потоки')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлен')

    @property
    def added(self) -> str:
        output = []
        if self.weeks:
            output.append(f'Н:{self.weeks.count()}')
        if self.enrollments:
            output.append(f'П:{self.enrollments.count()}')
        return ', '.join(output)

    def __str__(self) -> str:
        return f'{self.name}'

    class Meta:
        verbose_name = 'Программа'
        verbose_name_plural = 'Программы'
        ordering = ('course', 'created_at')
        get_latest_by = 'created_at'
