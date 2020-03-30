from django.db import models


class Hatim(models.Model):

    finished = models.BooleanField(verbose_name='Завершено', default=False)

    def save(self, *args, **kwargs):
        super(Hatim, self).save(*args, **kwargs)
        for i in range(30):
            Juz.objects.create(hatim=self)

    def __str__(self):
        return 'Hatim {}'.format(self.pk)


class Juz(models.Model):

    hatim = models.ForeignKey(Hatim, verbose_name='Хатим', on_delete=models.CASCADE)
    STATUS = ((1, 'Свободен'), (2, 'Читается'), (3, 'Завершен'))
    status = models.PositiveSmallIntegerField(verbose_name='Статус', choices=STATUS, default=1)

    @property
    def number(self):
        n = self.pk % 30
        if not n:
            n = 30
        return n

    def __str__(self):
        return 'Juz {} | {}'.format(self.number, self.hatim)

    class Meta:
        ordering = ['pk']

class Reader(models.Model):
    tg_id = models.IntegerField(verbose_name='Telegram ID', null=True, blank=True)
    taken_juz = models.OneToOneField(Juz, verbose_name='Взял главу', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return str(self.tg_id)