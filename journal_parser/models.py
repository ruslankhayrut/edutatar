from django.db import models

# Create your models here.
class Login(models.Model):
    login_int = models.CharField(verbose_name='Логин', max_length=100)
    reg_date = models.DateTimeField(verbose_name='Дата регистрации')

    def __str__(self):
        return self.login_int
