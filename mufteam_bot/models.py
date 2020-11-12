from django.db import models


class Student(models.Model):
    telegram_id = models.PositiveIntegerField()


class Subject(models.Model):
    name = models.CharField(max_length=50)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    marks_string = models.TextField(default='')
    homework = models.TextField(default='')

    @property
    def average_mark(self):
        marks = [int(num) for num in self.marks_string.split(', ')]
        if len(marks) < 3:
            return 'Недостаточно оценок'
        return round(sum(marks) / len(marks), 2)
