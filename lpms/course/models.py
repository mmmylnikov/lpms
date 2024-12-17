from datetime import datetime

from django.db import models
from django.urls import reverse_lazy

from user.models import User


class Course(models.Model):
    name = models.CharField(max_length=128, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    tg_chat = models.CharField(max_length=256, verbose_name='Телеграм чат',
                               blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлен')

    @property
    def slug(self) -> str:
        return f"{''.join([s[0].upper() for s in self.name.split(' ')])}"

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return f'{reverse_lazy("home")}?course={self.pk}'

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
        ordering = ('name', )
        get_latest_by = 'created_at'


class Enrollment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.PROTECT,
                               verbose_name='Курс')
    number = models.PositiveSmallIntegerField(verbose_name='Номер')
    start = models.DateField(verbose_name='Старт')
    finish = models.DateField(verbose_name='Финиш')
    tg_chat = models.CharField(max_length=256, verbose_name='Телеграм чат',
                               blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлен')

    @property
    def slug(self) -> str:
        title_words = self.course.name.split(' ')
        return f"{''.join([s[0].upper() for s in title_words])}{self.number}"

    @property
    def is_completed(self) -> bool:
        return self.finish < datetime.now().date()
    is_completed.fget.boolean = True  # type: ignore
    is_completed.fget.short_description = 'Завершен'  # type: ignore

    def __str__(self) -> str:
        return self.slug

    class Meta:
        verbose_name = 'Поток'
        verbose_name_plural = 'Потоки'
        ordering = ('-finish', )
        get_latest_by = 'finish'


class Team(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.PROTECT,
                                   verbose_name='Поток')
    tutor = models.ForeignKey(User, on_delete=models.PROTECT,
                              verbose_name='Куратор', related_name='tutor')
    students = models.ManyToManyField(User, verbose_name='Студенты',
                                      blank=True)
    tg_chat = models.CharField(max_length=256, verbose_name='Телеграм чат',
                               blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлен')

    @property
    def name(self) -> str:
        return f'{self.enrollment.slug} (куратор {self.tutor.get_full_name()})'

    @property
    def slug(self) -> str:
        return f'{self.enrollment.slug}_{self.pk}'.lower()

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'
        ordering = ('-enrollment', )
        get_latest_by = 'created_at'


class Track(models.Model):
    name = models.CharField(max_length=128, verbose_name='Название')
    course = models.ForeignKey(Course, on_delete=models.PROTECT,
                               verbose_name='Курс')
    description = models.TextField(verbose_name='Описание')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлен')

    def __str__(self) -> str:
        return f'{self.course.slug} - {self.name}'

    def slug(self) -> str:
        return f"{''.join([s[0].upper() for s in self.name.split(' ')])}"

    class Meta:
        verbose_name = 'Трек'
        verbose_name_plural = 'Треки'
        ordering = ('created_at', )
        get_latest_by = 'created_at'
