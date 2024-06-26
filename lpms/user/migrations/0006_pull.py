# Generated by Django 5.0.3 on 2024-04-02 19:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0005_repo'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pull',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.SmallIntegerField(verbose_name='Номер')),
                ('title', models.CharField(max_length=1024, verbose_name='Название')),
                ('url', models.CharField(max_length=1024, verbose_name='URL')),
                ('html_url', models.CharField(max_length=1024, verbose_name='HTML URL')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Создан')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Обновлен')),
                ('repo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='user.repo', verbose_name='Репозиторий')),
            ],
            options={
                'verbose_name': 'Пулл-реквест',
                'verbose_name_plural': 'Пулл-реквесты',
                'ordering': ('-created_at',),
                'get_latest_by': 'created_at',
            },
        ),
    ]
