# Generated by Django 3.0.3 on 2020-02-18 07:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0002_auto_20200218_1013'),
    ]

    operations = [
        migrations.AlterField(
            model_name='day',
            name='number',
            field=models.PositiveSmallIntegerField(unique=True, verbose_name='День недели (1-7)'),
        ),
    ]
