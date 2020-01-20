# Generated by Django 3.0.2 on 2020-01-19 19:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vosp_bot', '0002_auto_20200113_1352'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='vosp',
            options={'ordering': ['name'], 'verbose_name': 'Воспитатель', 'verbose_name_plural': 'Воспитатели'},
        ),
        migrations.AddField(
            model_name='vosp',
            name='telegram_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='Telegram ID'),
        ),
        migrations.AlterField(
            model_name='vosp',
            name='lunch_duty_day',
            field=models.DateField(blank=True, null=True, unique=True, verbose_name='Дата дежурства на ужин'),
        ),
        migrations.AlterField(
            model_name='vosp',
            name='tea_duty_day1',
            field=models.DateField(blank=True, null=True, unique=True, verbose_name='Дата первого дежурства к чаю'),
        ),
        migrations.AlterField(
            model_name='vosp',
            name='tea_duty_day2',
            field=models.DateField(blank=True, null=True, unique=True, verbose_name='Дата второго дежурства к чаю'),
        ),
        migrations.CreateModel(
            name='Mutfak',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(unique=True, verbose_name='Дата дежурства в мутфаке')),
                ('vosp1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='duty1', to='vosp_bot.Vosp', verbose_name='Дежурный 1')),
                ('vosp2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='duty2', to='vosp_bot.Vosp', verbose_name='Дежурный 2')),
            ],
            options={
                'verbose_name': 'Дежурство в мутфаке',
                'verbose_name_plural': 'Дежурства в мутфаке',
                'ordering': ['date'],
            },
        ),
    ]
