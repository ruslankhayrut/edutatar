from django.db import models


class Hatim(models.Model):

    finished = models.BooleanField(verbose_name='Завершено', default=False)

    def save(self, *args, **kwargs):
        super(Hatim, self).save(*args, **kwargs)
        if not Juz.objects.filter(hatim=self):
            Juz.objects.create(hatim=self, number=1)

    def __str__(self):
        return 'Hatim {}'.format(self.pk)


class Juz(models.Model):

    hatim = models.ForeignKey(Hatim, verbose_name='Хатим', on_delete=models.CASCADE)
    STATUS = ((1, 'Свободен'), (2, 'Читается'), (3, 'Завершен'))
    status = models.PositiveSmallIntegerField(verbose_name='Статус', choices=STATUS, default=1)
    number = models.PositiveSmallIntegerField(verbose_name='Номер', null=True)


    def __str__(self):
        return 'Juz {}'.format(self.number)

    class Meta:
        ordering = ['hatim', 'number']

class Reader(models.Model):
    tg_id = models.IntegerField(verbose_name='Telegram ID', null=True, blank=True)
    taken_juz = models.OneToOneField(Juz, verbose_name='Взял главу', on_delete=models.SET_NULL, blank=True, null=True)
    take_date = models.DateTimeField(verbose_name='Дата взятия главы', null=True, blank=True)

    def __str__(self):
        return str(self.tg_id)

class HCount(models.Model):

    value = models.PositiveSmallIntegerField(verbose_name='Значение', default=0)

    def __str__(self):
        return 'Счетчик завершенных книг'