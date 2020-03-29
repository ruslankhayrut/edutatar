from django.shortcuts import render, HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from .config import token, owner_id
from .models import *
import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
import requests
import datetime
import time


bot = telebot.TeleBot(token)
keyboard = InlineKeyboardMarkup()

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
        return render(request, 'journal_parser/index.html')


def set_webhook(request):
    URL1 = 'https://api.telegram.org/bot{}/setWebhook?'.format(token)
    URL2 = 'url=https://features.li79.ru/sharebot/{}'.format(token)
    r = requests.post('https://api.telegram.org/bot{}/deleteWebhook'.format(token))
    r = r.json()
    if r['ok']:
        s = requests.post(URL1 + URL2)
        s = s.json()
        if s['ok']:
            bot.send_message(owner_id, 'Webhook was set')
            return HttpResponse('<h1>Bot greets you</h1>')
    return HttpResponse('<h1>Something went wrong</h1>')

@bot.callback_query_handler(func=lambda c: c.data.split('/')[0] == 'take')
def take_juz(callback_query: CallbackQuery):
    user = callback_query.from_user.id

    juz_id = callback_query.data.split('/')[-1]


    taken_juz = Juz.objects.get(pk=juz_id)
    taken_juz.status = 2
    taken_juz.save()

    bot.answer_callback_query(callback_query.id)
    bot.send_message(user, 'Вы взяли {} главу!'.format(taken_juz.number))



@bot.message_handler(commands=['take'])
def take(message):

    user = message.chat.id
    latest_hatim = Hatim.objects.latest('pk')

    free_juzes = Juz.objects.filter(hatim=latest_hatim, status=1)

    if free_juzes:
        juz = free_juzes[0]

    else:
        new_hatim = Hatim.objects.create()
        juz = Juz.objects.filter(hatim=new_hatim)

    take_btn = InlineKeyboardButton('Взять {} главу'.format(juz.number), callback_data='take/{}'.format(juz.id))
    keyboard.add(take_btn)
    bot.send_message(user, '{} глава'.format(juz.number), reply_markup=keyboard)



@bot.message_handler(content_types=['text'])
def text_handler(message):
    text = message.text
    if text.lower() == 'мой id':
        bot.send_message(message.chat.id, str(message.chat.id))
    else:
        bot.send_message(message.chat.id, message.text)

