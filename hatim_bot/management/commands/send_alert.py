from hatim_bot.models import Reader
from hatim_bot.views import bot
from django.core.management.base import BaseCommand
from telebot.apihelper import ApiException
from hatim_bot.config import owner_id

class Command(BaseCommand):

    def handle(self, *args, **options):

        for reader in Reader.objects.all():

            msg = 'Добрый день, дорогие читатели :)\n\nТеперь можно не только посмотреть, сколько глав вы прочитали, ' \
                  'но и увидеть, какое место вы занимаете в общем рейтинге. ' \
                  'Для этого используйте уже известную команду /mystats \n\n' \
                  'P.S. Надеемся на вашу активность в ближайшее время 😉'
            try:
                bot.send_message(reader.tg_id, msg, parse_mode='Markdown', disable_notification=True)
                print("Sent to", reader.tg_id)
            except ApiException:
                print('This user blocked the bot', reader.tg_id)
        print("Done")

