from vosp_bot.views import bot
from vosp_bot.config import owner_id
import time
from django.core.management.base import BaseCommand

class Command(BaseCommand):

    def handle(self, *args, **options):
        bot.send_message(owner_id, "Boss, I'm working! {0}:{1}".format(time.localtime().tm_hour, time.localtime().tm_min))
