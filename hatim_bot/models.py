from django.db import models


class Reader(models.Model):
    phone = models.CharField(max_length=100, verbose_name='Телефон', null=True, blank=True)
    tg_id = models.IntegerField(verbose_name='Telegram ID', null=True, blank=True)

    def __str__(self):
        return self.name if self.name else self.pk


class Hatim(models.Model):

    def save(self, *args, **kwargs):
        super(Hatim, self).save(*args, **kwargs)
        for i in range(30):
            Juz.objects.create(hatim=self)

    def __str__(self):
        return 'Hatim {}'.format(self.pk)


class Juz(models.Model):

    hatim = models.ForeignKey(Hatim, verbose_name='Хатим', on_delete=models.CASCADE)
    reader = models.OneToOneField(Reader, verbose_name='Читает', on_delete=models.CASCADE, blank=True, null=True)
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
