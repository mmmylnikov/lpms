# Generated by Django 5.0.3 on 2024-04-08 15:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notify', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='provider',
            name='name',
            field=models.CharField(choices=[('telegram_bot', 'TELEGRAM_BOT')], max_length=64, unique=True, verbose_name='Название'),
        ),
    ]
