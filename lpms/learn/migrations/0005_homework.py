# Generated by Django 5.0.3 on 2024-03-23 18:47

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learn', '0004_alter_lesson_options_challenge'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Homework',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField(blank=True, null=True, verbose_name='Комментарий')),
                ('repo', models.CharField(blank=True, max_length=512, null=True, verbose_name='Репозиторий')),
                ('status', models.CharField(choices=[('available', 'Доступно к выполнению'), ('execution', 'Выполнение'), ('review', 'На проверке'), ('correction', 'Требует исправлений'), ('approved', 'Принято')], max_length=11, verbose_name='Статус')),
                ('track', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
                ('сhallenge', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='learn.challenge', verbose_name='Задание')),
            ],
        ),
    ]