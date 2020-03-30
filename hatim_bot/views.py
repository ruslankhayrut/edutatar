from django.shortcuts import render, HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from .config import token, owner_id
from .models import *
import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, \
    ReplyKeyboardMarkup, ReplyKeyboardRemove, \
    KeyboardButton, CallbackQuery
import requests
import datetime
import time


bot = telebot.TeleBot(token)
inline_keyboard = InlineKeyboardMarkup()
reply_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

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
    reader = Reader.objects.get(tg_id=user)

    juz_id = callback_query.data.split('/')[-1]

    taken_juz = Juz.objects.get(pk=juz_id)
    taken_juz.status = 2
    taken_juz.save()

    reader.taken_juz = taken_juz
    reader.save()

    bot.answer_callback_query(callback_query.id)

    button1 = KeyboardButton('Я прочитал {} главу'.format(taken_juz.number))
    button2 = KeyboardButton('Отказаться от главы')
    reply_keyboard.add(button1, button2)

    bot.send_message(user, 'Вы взяли {} главу'.format(taken_juz.number), reply_markup=reply_keyboard)

@bot.message_handler(commands=['start'])
def start(message):
    user = message.chat.id

    reader, created = Reader.objects.get_or_create(tg_id=user)

    if reader.taken_juz:
        button1 = KeyboardButton('Я прочитал {} главу'.format(reader.taken_juz.number))
        button2 = KeyboardButton('Отказаться от главы')
        reply_keyboard.add(button1, button2)
    else:
        button = KeyboardButton('Взять главу')
        reply_keyboard.add(button)

    bot.send_message(user, 'Hello', reply_markup=reply_keyboard)


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
    inline_keyboard.add(take_btn)
    bot.send_message(user, '{} глава'.format(juz.number), reply_markup=inline_keyboard)

def finish(user, reader, juz_id):
    finished_juz = Juz.objects.get(pk=juz_id)
    finished_juz.status = 3
    finished_juz.save()

    reader.taken_juz = None
    reader.save()

    button = KeyboardButton('Взять главу')
    reply_keyboard.add(button)

    bot.send_message(user, 'Спасибо 👍', reply_markup=reply_keyboard)

def reject(user, reader, juz_id):
    rej_juz = Juz.objects.get(pk=juz_id)
    rej_juz.status = 1
    rej_juz.save()

    reader.taken_juz = None
    reader.save()

    button = KeyboardButton('Взять главу')
    reply_keyboard.add(button)

    bot.send_message(user, 'Жаль 😔', reply_markup=reply_keyboard)

@bot.message_handler(content_types=['text'])
def text_handler(message):
    text = message.text
    user = message.chat.id
    reader = Reader.objects.get(tg_id=user)
    taken_juz = reader.taken_juz

    if text == 'Взять главу':
        take(message)
    elif taken_juz and text == 'Я прочитал {} главу'.format(taken_juz.number):
        finish(user, reader, taken_juz.id)
    elif taken_juz and text == 'Отказаться от главы':
        reject(user, reader, taken_juz.id)
    else:
        bot.send_message(message.chat.id, message.text)

