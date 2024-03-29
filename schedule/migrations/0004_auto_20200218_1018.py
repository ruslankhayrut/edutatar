# Generated by Django 3.0.3 on 2020-02-18 07:18

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("schedule", "0003_auto_20200218_1014"),
    ]

    operations = [
        migrations.AlterField(
            model_name="day",
            name="number",
            field=models.PositiveSmallIntegerField(
                unique=True,
                validators=[
                    django.core.validators.MaxValueValidator(
                        7, "Введите корректный номер дня"
                    ),
                    django.core.validators.MinValueValidator(
                        1, "Введите корректный номер дня"
                    ),
                ],
                verbose_name="День недели (1-7)",
            ),
        ),
    ]
