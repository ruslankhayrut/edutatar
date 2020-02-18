# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Break',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('start_time', models.TimeField(verbose_name='Время начала', blank=True, null=True)),
                ('duration', models.PositiveSmallIntegerField(verbose_name='Длительность (мин)', blank=True, null=True, default=10)),
            ],
        ),
        migrations.CreateModel(
            name='Day',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('number', models.PositiveSmallIntegerField(verbose_name='День недели (1-7)', blank=True, null=True, default=1)),
                ('alt_message', models.TextField(verbose_name='Альтернативный текст', blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Lesson',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('number', models.PositiveSmallIntegerField(verbose_name='Номер урока', blank=True, null=True)),
                ('start_time', models.TimeField(verbose_name='Время начала', blank=True, null=True)),
                ('duration', models.PositiveSmallIntegerField(verbose_name='Длительность (мин)', blank=True, null=True, default=45)),
            ],
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(verbose_name='Название расписания', max_length=100, blank=True, null=True)),
                ('breaks', models.ForeignKey(verbose_name='Перемены', to='schedule.Break', on_delete=models.CASCADE)),
                ('lessons', models.ForeignKey(verbose_name='Уроки', to='schedule.Lesson', on_delete=models.CASCADE)),
            ],
        ),
        migrations.AddField(
            model_name='day',
            name='schedule',
            field=models.OneToOneField(verbose_name='Расписание', to='schedule.Schedule', on_delete=models.CASCADE),
        ),
    ]
