from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .config import token, owner_id, hook_url
from .models import *
from hatim_bot.helpers import create_standings_table
import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, \
    ReplyKeyboardMarkup, KeyboardButton, CallbackQuery
import requests
import time


bot = telebot.TeleBot(token)
take_chapter_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
take_chapter_keyboard.add(KeyboardButton('Взять главу'))

finish_reject_kb = ReplyKeyboardMarkup(resize_keyboard=True)
finish_reject_kb.add(KeyboardButton('Я прочитал главу'), KeyboardButton('Отказаться от главы'))


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
    URL2 = 'url={}/sharebot/{}'.format(hook_url, token)
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
        data = callback_query.data.split('/')
        juz_num, hatim_id = data[1], data[2]

        hatim = Hatim.objects.get(pk=hatim_id)

        taken_juz, created = Juz.objects.get_or_create(hatim=hatim, number=juz_num)

        if taken_juz.status == 1:

            taken_juz.set_status(2)
            reader.take_juz(taken_juz)

            bot.send_message(user, 'Вы взяли {} главу'.format(juz_num), reply_markup=finish_reject_kb)
        else:
            bot.send_message(user, 'Извините, эту главу уже взяли. Пожалуйста, выберите другую.')
    else:
        bot.send_message(user, 'Вы уже взяли главу {}'.format(reader.taken_juz.number))

    bot.answer_callback_query(callback_query.id)

@bot.message_handler(commands=['start'])
def start(message):
    user = message.chat.id

    reader, created = Reader.objects.get_or_create(tg_id=user)

    reply_keyboard = take_chapter_keyboard
    if reader.taken_juz:
        reply_keyboard = finish_reject_kb

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


@bot.message_handler(commands=['mystats'])
def show_stats(message):

    user = message.chat.id
    reader = Reader.objects.get(tg_id=user)
    all_readers = Reader.objects.order_by('-read_counter')

    msg = create_standings_table(reader, all_readers)
    bot.send_message(user, msg, parse_mode='Markdown')


def take(user):

    not_finished_hatims = Hatim.objects.filter(finished=False)

    inline_keyboard = InlineKeyboardMarkup(row_width=5)

    for hatim in not_finished_hatims:
        this_juzes = Juz.objects.filter(hatim=hatim)
        can_take = sorted(list(set(range(1, 31)).difference(set((juz.number for juz in this_juzes if juz.status in (2, 3))))))

        if can_take:
            inline_keyboard.add(*map(lambda juz_n: InlineKeyboardButton('{}'.format(juz_n), callback_data='take/{}/{}'.format(juz_n, hatim.id)), can_take))
            break

    bot.send_message(user, 'Выберите главу', reply_markup=inline_keyboard)


def finish(reader, juz_id):
    finished_juz = Juz.objects.get(pk=juz_id)
    finished_juz.set_status(3)
    msg = 'Спасибо!'

    fin = finished_juz.hatim.check_finished()

    if fin:
        counter = HCount.objects.get()
        counter.increment()
        msg += '\nВы дочитали последнюю главу книги. Пожалуйста, прочитайте дополнительный контент.'

    reader.increment_counter()
    reader.take_juz(None)

    bot.send_message(reader.tg_id, msg, reply_markup=take_chapter_keyboard)


def reject(reader, juz_id):
    rej_juz = Juz.objects.get(pk=juz_id)
    rej_juz.set_status(1)

    reader.take_juz(None)

    bot.send_message(reader.tg_id, 'Жаль =(', reply_markup=take_chapter_keyboard)


@bot.message_handler(content_types=['text'])
def text_handler(message):
    text = message.text
    user = message.chat.id
    reader = Reader.objects.get(tg_id=user)
    taken_juz = reader.taken_juz

    if text == 'Взять главу':
        take(user)
    elif taken_juz and text.startswith('Я прочитал'):
        finish(reader, taken_juz.id)
    elif taken_juz and text == 'Отказаться от главы':
        reject(reader, taken_juz.id)
    else:
        bot.send_message(message.chat.id, message.text)

