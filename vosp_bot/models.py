from django.db import models


class Vosp(models.Model):

    name = models.CharField(verbose_name='Имя, фамилия', max_length=100)
    lunch_duty_day = models.DateField(verbose_name='Дата дежурства на ужин', blank=True, null=True)
    tea_duty_day1 = models.DateField(verbose_name='Дата первого дежурства к чаю', blank=True, null=True)
    tea_duty_day2 = models.DateField(verbose_name='Дата второго дежурства к чаю', blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta():
        verbose_name = 'Воспитатель'
        verbose_name_plural = 'Воспитатели'