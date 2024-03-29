# Generated by Django 3.0.3 on 2020-11-12 16:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("schedule", "0008_auto_20200218_1312"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="day",
            options={
                "ordering": ["number"],
                "verbose_name": "День недели",
                "verbose_name_plural": "Дни недели",
            },
        ),
        migrations.AlterModelOptions(
            name="schedule",
            options={
                "verbose_name": "Шаблон расписания",
                "verbose_name_plural": "Шаблоны расписаний",
            },
        ),
        migrations.AlterField(
            model_name="day",
            name="schedule",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.SET(None),
                to="schedule.Schedule",
                verbose_name="Расписание",
            ),
        ),
    ]
