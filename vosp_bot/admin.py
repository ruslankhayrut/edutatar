from django.contrib import admin
from .models import Vosp, Mutfak




class VospAdmin(admin.ModelAdmin):

    list_display = ('name',
              'lunch_duty_day',
              'tea_duty_day1',
              'tea_duty_day2',
              )

class MutfakAdmin(admin.ModelAdmin):

    list_display = ('date', 'vosp1', 'vosp2')

admin.site.register(Vosp, VospAdmin)
admin.site.register(Mutfak, MutfakAdmin)