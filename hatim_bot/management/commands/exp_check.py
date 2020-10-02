from hatim_bot.models import Reader
from hatim_bot.views import bot
from hatim_bot.constants import EXPIRATION_TERM
import datetime
from django.core.management.base import BaseCommand
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import pytz

class Command(BaseCommand):

    def handle(self, *args, **options):

        utc = pytz.UTC
        reply_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        readers = Reader.objects.exclude(take_date=None).order_by('take_date')

        revoked = []
        warned = []

        for reader in readers:
            user_id = reader.tg_id
            td = reader.take_date
            now = utc.localize(datetime.datetime.now())
            if td + datetime.timedelta(days=EXPIRATION_TERM, hours=3) < now:

                reader.taken_juz.status = 1
                reader.taken_juz.save()

                reader.taken_juz = None
                reader.take_date = None
                reader.save()

                button = KeyboardButton('Взять главу')
                reply_keyboard.add(button)


                bot.send_message(user_id, 'К сожалению, вы слишком долго читали главу и мы отдали ее другому =(', reply_markup=reply_keyboard)
                revoked.append(user_id)
            elif td + datetime.timedelta(days=EXPIRATION_TERM - 1) < now:

                bot.send_message(user_id, 'У вас остался 1 день, чтобы завершить главу. '
                                           'Иначе она будет отдана другому. Пожалуйста, поторопитесь!')

                warned.append(user_id)



