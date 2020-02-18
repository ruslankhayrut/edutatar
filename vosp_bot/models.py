from django.db import models


class Vosp(models.Model):

    name = models.CharField(verbose_name='Имя, фамилия', max_length=100)
    telegram_id = models.IntegerField(verbose_name='Telegram ID', null=True, blank=True)
    lunch_duty_day = models.DateField(verbose_name='Дата дежурства на ужин', blank=True, null=True, unique=True)
    tea_duty_day1 = models.DateField(verbose_name='Дата первого дежурства к чаю', blank=True, null=True, unique=True)
    tea_duty_day2 = models.DateField(verbose_name='Дата второго дежурства к чаю', blank=True, null=True, unique=True)

    def __str__(self):
        return self.name



    class Meta:
        verbose_name = 'Воспитатель'
        verbose_name_plural = 'Воспитатели'
        ordering = ['name']

class Mutfak(models.Model):

    date = models.DateField(verbose_name='Дата дежурства в мутфаке', unique=True)
    vosp1 = models.ForeignKey(Vosp, on_delete=models.CASCADE, related_name='duty1', verbose_name='Дежурный 1')
    vosp2 = models.ForeignKey(Vosp, on_delete=models.CASCADE, related_name='duty2', verbose_name='Дежурный 2')

    class Meta:
        verbose_name = 'Дежурство в мутфаке'
        verbose_name_plural = 'Дежурства в мутфаке'
        ordering = ['date']

    def __str__(self):
        return str(self.date)