from vosp_bot.views import bot
from vosp_bot.config import owner_id
from vosp_bot.models import Vosp
import datetime
from django.core.management.base import BaseCommand

def set_new_lunch_d(last):
    if last.isoweekday() == 4:
        return last + datetime.timedelta(days=3)
    else:
        return last + datetime.timedelta(days=1)

class Command(BaseCommand):


    def handle(self, *args, **options):
        queue = Vosp.objects.exclude(lunch_duty_day=None).order_by('lunch_duty_day')
        old, last = queue[0], queue[-1]
        if old.lunch_duty_day < datetime.date.today():
            old.lunch_duty_day = set_new_lunch_d(last.lunch_duty_day)
            old.save()
            bot.send_message(owner_id, 'Дежурство на ужин обновлено')
        else:
            bot.send_message(owner_id, 'Дежурство на ужин не обновлено')
