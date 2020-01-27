from vosp_bot.views import bot
from vosp_bot.config import owner_id
from vosp_bot.models import Vosp
import datetime
from django.core.management.base import BaseCommand

class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            duty = Vosp.objects.get(tea_duty_day1=datetime.date.today())
            if duty.telegram_id:
                bot.send_message(duty.telegram_id, 'Не забудьте купить вещи к чаю')
                bot.send_message(owner_id, 'Напоминание к чаю отправлено {}'.format(duty.name))
            else:
                bot.send_message(owner_id, 'Не получилось отправить напоминание к чаю {}, т.к. он не подписан'.format(duty.name))

        except Vosp.DoesNotExist:
            try:
                duty = Vosp.objects.get(tea_duty_day2=datetime.date.today())
                if duty.telegram_id:
                    bot.send_message(duty.telegram_id, 'Не забудьте купить вещи к чаю')
                    bot.send_message(owner_id, 'Напоминание к чаю отправлено {}'.format(duty.name))
                else:
                    bot.send_message(owner_id,
                                     'Не получилось отправить напоминание к чаю {}, т.к. он не подписан'.format(
                                         duty.name))

            except Vosp.DoesNotExist:
                bot.send_message(owner_id, 'Не получилось отправить напоминание к чаю')

