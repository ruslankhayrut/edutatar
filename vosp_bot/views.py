from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .config import token, owner_id
from .models import Vosp, Mutfak
import telebot
import requests
import locale
import datetime
import time
locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')

bot = telebot.TeleBot(token)

@csrf_exempt
def index(request):
    if request.method == 'POST':
        if request.META.get('CONTENT_TYPE') == 'application/json':
            json_string = request.body.decode('utf-8')
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
            time.sleep(0.2)

            return HttpResponse('')
        return HttpResponse(status=200)
    else:
        return render(request, 'vosp_bot/index.html')


def set_webhook(request):
    URL1 = 'https://api.telegram.org/bot{}/setWebhook?'.format(token)
    URL2 = 'url=https://features.li79.ru/vospbot/{}'.format(token)
    r = requests.post('https://api.telegram.org/bot{}/deleteWebhook'.format(token))
    r = r.json()
    if r['ok']:
        s = requests.post(URL1 + URL2)
        s = s.json()
        if s['ok']:
            bot.send_message(owner_id, 'Webhook was set')
            return HttpResponse('<h1>Bot greets you</h1>')
    return HttpResponse('<h1>Something went wrong</h1>')


def date_to_str(date):
    return datetime.datetime.strftime(date, '%A %d %b')



@bot.message_handler(commands=['lunch'])
def show_lunch_queue(message):
    user = message.chat.id
    if Vosp.objects.get(telegram_id=user):
        queue = Vosp.objects.exclude(lunch_duty_day=None).order_by('lunch_duty_day')
        msg = 'Список на ближайшие 10 дней:'
        for v in queue:
            msg += '\n\n*{0}* покупает на ужин в {1}'.format(v.name, date_to_str(v.lunch_duty_day))
        bot.send_message(user, msg, parse_mode='markdown')

    else:
        bot.send_message(user, 'Доступ запрещен')


@bot.message_handler(commands=['evening'])
def show_evening_queue(message):
    user = message.chat.id
    if Vosp.objects.get(telegram_id=user):
        queue = Vosp.objects.exclude(tea_duty_day1=None, tea_duty_day2=None).order_by('tea_duty_day1')
        msg = 'Очередь к чаю:'
        for v in queue:
            msg += '\n\n*{0}* покупает в {1} и в {2}'.format(v.name, date_to_str(v.tea_duty_day1), date_to_str(v.tea_duty_day2))
        bot.send_message(user, msg, parse_mode='markdown')

    else:
        bot.send_message(user, 'Доступ запрещен')


@bot.message_handler(commands=['myschedule'])
def show_my_schedule(message):
    user = message.chat.id
    v = Vosp.objects.get(telegram_id=user)
    if v:
        msg = 'Вы покупаете на ужин в *{0}*\n\n' \
              'Вы покупаете к чаю в *{1}* и в *{2}*'.format(date_to_str(v.lunch_duty_day), date_to_str(v.tea_duty_day1), date_to_str(v.tea_duty_day2))
        bot.send_message(user, msg, parse_mode='markdown')
    else:
        bot.send_message(user, 'Доступ запрещен')

@bot.message_handler(commands=['mutfak'])
def show_mutfak_schedule(message):
    user = message.chat.id
    if Vosp.objects.get(telegram_id=user):
        queue = Mutfak.objects.all()
        msg = 'Примерное расписание дежурств в мутфаке:'
        for m in queue:
            msg += '\n\n*{0}* {1} и {2}'.format(' '.join(el for el in date_to_str(m.date).split()[1:]), m.vosp1, m.vosp2)
        bot.send_message(user, msg, parse_mode='markdown')
    else:
        bot.send_message(user, 'Доступ запрещен')



@bot.message_handler(content_types=['text'])
def text_handler(message):
    text = message.text
    if text.lower() == 'мой id':
        bot.send_message(message.chat.id, str(message.chat.id))
    else:
        bot.send_message(message.chat.id, message.text)


