from django.db import models
from markdown import markdown

from user.models import User
from course.models import Track, Course, Enrollment


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
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлен')

    @property
    def video_uid(self) -> str | None:
        if not self.video:
            return None
        return self.video.replace('https://www.youtube.com/watch?v=', '')

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
        return f'{self.track} - {self.name}'

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'
        ordering = ('track', 'created_at', 'name', )
        get_latest_by = 'created_at'


class Challenge(models.Model):
    track = models.ForeignKey(Track, on_delete=models.PROTECT,
                              verbose_name='Трек')
    name = models.CharField(max_length=128, verbose_name='Название')
    content = models.TextField(verbose_name='Контент', null=True, blank=True)
    repo = models.CharField(max_length=512, null=True, blank=True,
                            verbose_name='Репозиторий')
    url = models.CharField(max_length=512, null=True, blank=True,
                           verbose_name='Ссылка')
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
        return f'{self.track} - {self.name}'

    class Meta:
        verbose_name = 'Задание'
        verbose_name_plural = 'Задания'
        ordering = ('track', 'created_at', 'name', )
        get_latest_by = 'created_at'


class Homework(models.Model):
    status_choices = (
        ("available", "Доступно к выполнению"),
        ("execution", "Выполнение"),
        ("review", "На проверке"),
        ("correction", "Требует исправлений"),
        ("approved", "Принято"),
    )
    user = models.ForeignKey(User, on_delete=models.PROTECT,
                             verbose_name='Пользователь')
    сhallenge = models.ForeignKey(Challenge, on_delete=models.PROTECT,
                                  verbose_name='Задание')
    comment = models.TextField(null=True, blank=True,
                               verbose_name='Комментарий')
    repo = models.CharField(max_length=512, null=True, blank=True,
                            verbose_name='Репозиторий')
    status = models.CharField(max_length=11, choices=status_choices,
                              verbose_name='Статус')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлен')

    def __str__(self) -> str:
        return f'{self.сhallenge} ({self.user.get_full_name()})'

    class Meta:
        verbose_name = 'Работа'
        verbose_name_plural = 'Работы'
        ordering = ('-created_at', )
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
        return f'{self.course} #{self.number}'

    class Meta:
        verbose_name = 'Неделя'
        verbose_name_plural = 'Недели'
        ordering = ('course', 'number')
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
