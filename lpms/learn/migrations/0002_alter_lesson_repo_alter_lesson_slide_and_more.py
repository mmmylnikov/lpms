# Generated by Django 5.0.3 on 2024-03-23 09:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learn', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lesson',
            name='repo',
            field=models.CharField(max_length=512, verbose_name='Репозиторий'),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='slide',
            field=models.CharField(max_length=512, verbose_name='Слайд'),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='url',
            field=models.CharField(max_length=512, verbose_name='Ссылка'),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='video',
            field=models.CharField(max_length=512, verbose_name='Видеоролик'),
        ),
    ]