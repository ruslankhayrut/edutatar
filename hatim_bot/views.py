from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .config import token, owner_id
from .models import *
import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, \
    ReplyKeyboardMarkup, KeyboardButton, CallbackQuery
from random import choice
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
    if not reader.taken_juz:
        juz_id = callback_query.data.split('/')[-1]

        taken_juz = Juz.objects.get(pk=juz_id)
        taken_juz.status = 2
        taken_juz.save()

        reader.taken_juz = taken_juz
        reader.take_date = datetime.datetime.now()
        reader.save()

        button1 = KeyboardButton('Я прочитал {} главу'.format(taken_juz.number))
        button2 = KeyboardButton('Отказаться от главы')
        reply_keyboard.add(button1, button2)

        bot.send_message(user, 'Вы взяли {} главу'.format(taken_juz.number), reply_markup=reply_keyboard)

    else:
        bot.send_message(user, 'Вы уже взяли главу {}'.format(reader.taken_juz.number))

    bot.answer_callback_query(callback_query.id)

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

    bot.send_message(user, 'Hello!', reply_markup=reply_keyboard)

@bot.message_handler(commands=['help'])
def help(message):
    user = message.chat.id

    help_text = 'Доступные команды:\n' \
                '/start\n' \
                '/help\n\n' \
                'Если вы взяли главу, а клавиатура вдруг не обновилась, отправьте боту сообщение ' \
                '"Я прочитал ... главу" (если вы прочитали эту главу) или ' \
                '"Отказаться от главы" (если вы хотите попробовать взять другую главу)\n\n' \
                'Если вы еще не взяли главу, а соответствующая кнопка почему-то не появилась, отправьте боту сообщение ' \
                '"Взять главу"'

    bot.send_message(user, help_text)

def take(user):

    not_finished_hatims = Hatim.objects.filter(finished=False)

    free_juzes = []
    for hatim in not_finished_hatims:
        free_juzes = Juz.objects.filter(hatim=hatim, status=1) #htm may be not finished but with no free juzes
        if free_juzes:
            break

    if free_juzes:
        juz1 = free_juzes[0]
        take_btn = InlineKeyboardButton('Взять {} главу'.format(juz1.number), callback_data='take/{}'.format(juz1.id))
        inline_keyboard.add(take_btn)

        if len(free_juzes) > 1:
            juz2 = choice(free_juzes[1:])
            take_btn2 = InlineKeyboardButton('Взять {} главу'.format(juz2.number), callback_data='take/{}'.format(juz2.id))
            inline_keyboard.add(take_btn2)

        bot.send_message(user, 'Выберите главу', reply_markup=inline_keyboard)

    else:
        bot.send_message(user, 'Упс...\nГлавы закончились и не успели обновиться. Пожалуйста, обратитесь к администратору.')

def finish(user, reader, juz_id):
    finished_juz = Juz.objects.get(pk=juz_id)
    finished_juz.status = 3
    finished_juz.save()

    msg = 'Спасибо!'

    hatim = finished_juz.hatim
    finished_juzes = Juz.objects.filter(hatim=hatim, status=3)

    if len(finished_juzes) == 30:
        hatim.finished = True
        hatim.save()
        counter = HCount.objects.get()
        counter.value += 1
        counter.save()
        msg += '\nВы дочитали последнюю главу книги. Пожалуйста, прочитайте дополнительный контент.'

    reader.taken_juz = None
    reader.take_date = None
    reader.save()

    button = KeyboardButton('Взять главу')
    reply_keyboard.add(button)

    bot.send_message(user, msg, reply_markup=reply_keyboard)



def reject(user, reader, juz_id):
    rej_juz = Juz.objects.get(pk=juz_id)
    rej_juz.status = 1
    rej_juz.save()

    reader.taken_juz = None
    reader.take_date = None
    reader.save()

    button = KeyboardButton('Взять главу')
    reply_keyboard.add(button)

    bot.send_message(user, 'Жаль =(', reply_markup=reply_keyboard)

@bot.message_handler(content_types=['text'])
def text_handler(message):
    text = message.text
    user = message.chat.id
    reader = Reader.objects.get(tg_id=user)
    taken_juz = reader.taken_juz

    if text == 'Взять главу':
        take(user)
    elif taken_juz and text == 'Я прочитал {} главу'.format(taken_juz.number):
        finish(user, reader, taken_juz.id)
    elif taken_juz and text == 'Отказаться от главы':
        reject(user, reader, taken_juz.id)
    else:
        bot.send_message(message.chat.id, message.text)

