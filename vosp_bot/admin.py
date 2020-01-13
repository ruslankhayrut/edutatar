from django.contrib import admin
from .models import Vosp


class VospAdmin(admin.ModelAdmin):

    list_display = ('name',
              'lunch_duty_day',
              'tea_duty_day1',
              'tea_duty_day2',
              )

admin.site.register(Vosp, VospAdmin)