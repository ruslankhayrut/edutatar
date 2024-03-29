# Generated by Django 3.0.2 on 2020-01-13 10:40

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Vosp",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100, verbose_name="Имя, фамилия")),
                (
                    "lunch_duty_day",
                    models.DateField(verbose_name="Дата дежурства на ужин"),
                ),
                (
                    "tea_duty_day1",
                    models.DateField(verbose_name="Дата первого дежурства к чаю"),
                ),
                (
                    "tea_duty_day2",
                    models.DateField(verbose_name="Дата второго дежурства к чаю"),
                ),
            ],
        ),
    ]
