from django.db import models
import datetime

class Hatim(models.Model):

    finished = models.BooleanField(verbose_name='Завершено', default=False)

    def save(self, *args, **kwargs):
        super(Hatim, self).save(*args, **kwargs)
        if not Juz.objects.filter(hatim=self):
            Juz.objects.create(hatim=self, number=1)

    def check_finished(self):

        fin = len(Juz.objects.filter(hatim=self, status=3)) == 30
        if fin:
            self.finished = True
            self.save()

            return True
        return False

    def __str__(self):
        return 'Hatim {}'.format(self.pk)


class Juz(models.Model):

    hatim = models.ForeignKey(Hatim, verbose_name='Хатим', on_delete=models.CASCADE)
    STATUS = ((1, 'Свободен'), (2, 'Читается'), (3, 'Завершен'))
    status = models.PositiveSmallIntegerField(verbose_name='Статус', choices=STATUS, default=1)
    number = models.PositiveSmallIntegerField(verbose_name='Номер', null=True)

    def set_status(self, status):
        self.status = status
        self.save()

    def __str__(self):
        return '{} | Juz {}'.format(self.hatim, self.number)

    class Meta:
        ordering = ['hatim', 'number']

class Reader(models.Model):
    tg_id = models.IntegerField(verbose_name='Telegram ID', null=True, blank=True)
    first_name = models.CharField(verbose_name='Имя', null=True, blank=True, max_length=50)
    last_name = models.CharField(verbose_name='Фамилия', null=True, blank=True, max_length=50)
    username = models.CharField(verbose_name='Username TG', null=True, blank=True, max_length=50)
    taken_juz = models.OneToOneField(Juz, verbose_name='Взял главу', on_delete=models.SET_NULL, blank=True, null=True)
    take_date = models.DateTimeField(verbose_name='Дата взятия главы', null=True, blank=True)
    reading_days = models.PositiveSmallIntegerField(verbose_name='Сколько дней читал', default=0)

    read_counter = models.PositiveSmallIntegerField(verbose_name='Прочитано глав', default=0)

    def increment_counter(self):
        self.read_counter += 1
        self.save()

    def take_juz(self, juz):
        self.taken_juz = juz
        self.take_date = datetime.datetime.now() if juz else None
        self.save()

    @property
    def exp_date(self):
        return self.take_date + datetime.timedelta(days=7) if self.take_date else None

    @property
    def reading_speed(self):
        if self.reading_days:
            return round(self.read_counter * 30 / self.reading_days, 2)
        return 0

    @property
    def fullname(self):
        return '{} {}'.format(self.first_name, self.last_name)

    def __str__(self):
        return str(self.tg_id)

class HCount(models.Model):

    value = models.PositiveSmallIntegerField(verbose_name='Значение', default=0)

    def increment(self):
        self.value += 1
        self.save()

    def __str__(self):
        return 'Счетчик завершенных книг'