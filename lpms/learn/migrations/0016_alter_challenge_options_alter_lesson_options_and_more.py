# Generated by Django 5.0.3 on 2024-07-13 10:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learn', '0015_lesson_order'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='challenge',
            options={'get_latest_by': 'created_at', 'ordering': ('track', 'order', 'name'), 'verbose_name': 'Задание', 'verbose_name_plural': 'Задания'},
        ),
        migrations.AlterModelOptions(
            name='lesson',
            options={'get_latest_by': 'created_at', 'ordering': ('track', 'order', 'name'), 'verbose_name': 'Урок', 'verbose_name_plural': 'Уроки'},
        ),
        migrations.AddField(
            model_name='challenge',
            name='order',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='Порядок'),
        ),
    ]