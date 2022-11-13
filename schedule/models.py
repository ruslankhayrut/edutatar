import datetime

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

# Create your models here.


class Schedule(models.Model):
    name = models.CharField(
        verbose_name="Название расписания", max_length=100, blank=True, null=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Шаблон расписания"
        verbose_name_plural = "Шаблоны расписаний"


class Lesson(models.Model):
    number = models.PositiveSmallIntegerField(
        verbose_name="Номер урока", blank=True, null=True
    )
    start_time = models.TimeField(verbose_name="Время начала", blank=True, null=True)
    duration = models.PositiveSmallIntegerField(
        verbose_name="Длительность (мин)", blank=True, null=True, default=45
    )
    schedule = models.ForeignKey(
        Schedule,
        on_delete=models.CASCADE,
        verbose_name="Расписание",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
        ordering = ["start_time"]

    @property
    def lesson_end(self):
        return (
            datetime.datetime.combine(datetime.date(1, 1, 1), self.start_time)
            + datetime.timedelta(minutes=self.duration)
        ).time()

    def __str__(self):
        return "Урок {0} | {1} - {2}".format(
            self.number, self.start_time, self.lesson_end
        )


class Break(models.Model):
    start_time = models.TimeField(verbose_name="Время начала", blank=True, null=True)
    duration = models.PositiveSmallIntegerField(
        verbose_name="Длительность (мин)", blank=True, null=True, default=10
    )
    schedule = models.ForeignKey(
        Schedule,
        on_delete=models.CASCADE,
        verbose_name="Расписание",
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = "Перемена"
        verbose_name_plural = "Перемены"
        ordering = ["start_time"]

    @property
    def break_end(self):
        return (
            datetime.datetime.combine(datetime.date(1, 1, 1), self.start_time)
            + datetime.timedelta(minutes=self.duration)
        ).time()

    def __str__(self):
        return "Перемена {0} - {1}".format(self.start_time, self.break_end)


class Day(models.Model):
    number = models.PositiveSmallIntegerField(
        verbose_name="День недели (1-7)",
        unique=True,
        validators=[
            MaxValueValidator(7, "Введите корректный номер дня"),
            MinValueValidator(1, "Введите корректный номер дня"),
        ],
    )

    schedule = models.ForeignKey(
        Schedule,
        verbose_name="Расписание",
        on_delete=models.SET(None),
        blank=True,
        null=True,
    )
    alt_message = models.TextField(
        verbose_name="Альтернативный текст", blank=True, null=True
    )

    @property
    def weekday_str(self):
        if self.number:
            return (
                "Понедельник",
                "Вторник",
                "Среда",
                "Четверг",
                "Пятница",
                "Суббота",
                "Воскресенье",
            )[self.number - 1]
        return ""

    def __str__(self):
        return self.weekday_str

    class Meta:
        verbose_name = "День недели"
        verbose_name_plural = "Дни недели"
        ordering = ["number"]
