from vosp_bot.views import bot
from vosp_bot.config import owner_id
from vosp_bot.models import Vosp
import datetime
from django.core.management.base import BaseCommand


class Command(BaseCommand):


    def handle(self, *args, **options):
        queue = Vosp.objects.exclude(tea_duty_day1=None, tea_duty_day2=None).order_by('tea_duty_day1')
        old, last = queue[0], queue[len(queue)-1]
        if old.tea_duty_day2 < datetime.date.today():
            old.tea_duty_day1 = last.tea_duty_day1 + datetime.timedelta(days=7)
            old.tea_duty_day2 = old.tea_duty_day1 + datetime.timedelta(days=4)
            old.save()
            bot.send_message(owner_id, 'Дежурство к чаю обновлено')
        else:
            bot.send_message(owner_id, 'Дежурство к чаю не обновлено')
