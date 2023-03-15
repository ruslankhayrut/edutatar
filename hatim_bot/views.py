import requests
import telebot
from django.http.response import JsonResponse
from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from telebot.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from hatim_bot.helpers import create_standings_table, grab_name

from .config import hook_url, owner_id, token
from .models import *

bot = telebot.TeleBot(token, threaded=False)
take_chapter_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
take_chapter_keyboard.add(KeyboardButton("Взять главу"))

finish_reject_kb = ReplyKeyboardMarkup(resize_keyboard=True)
finish_reject_kb.add(
    KeyboardButton("Я прочитал главу"), KeyboardButton("Отказаться от главы")
)


@csrf_exempt
@require_http_methods(["POST"])
def index(request):
    if request.META.get("CONTENT_TYPE") != "application/json":
        return HttpResponse(status=403)

    json_string = request.body.decode("utf-8")
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return JsonResponse({"status": "OK"}, status=200)


def set_webhook(request):
    bot.set_webhook(f"{hook_url}/sharebot/{token}")
    bot.send_message(owner_id, "webhook set")
    return JsonResponse({"status": "OK"}, status=200)


@bot.callback_query_handler(func=lambda c: c.data.split("/")[0] == "take")
def take_juz(callback: CallbackQuery):
    user_id = callback.from_user.id
    reader = Reader.objects.get(tg_id=user_id)

    if reader.taken_juz:
        bot.send_message(user_id, f"Вы уже взяли главу {reader.taken_juz.number}")
        bot.answer_callback_query(callback.id)
        return

    _, juz_num, hatim_id = callback.data.split("/")

    hatim = Hatim.objects.get(pk=hatim_id)

    taken_juz, created = Juz.objects.get_or_create(hatim=hatim, number=juz_num)

    if taken_juz.status != 1:
        bot.send_message(
            user_id, "Извините, эту главу уже взяли. Пожалуйста, выберите другую."
        )
        bot.answer_callback_query(callback.id)
        return

    taken_juz.set_status(2)
    reader.take_juz(taken_juz)

    bot.send_message(
        user_id, f"Вы взяли {juz_num} главу", reply_markup=finish_reject_kb
    )
    bot.answer_callback_query(callback.id)


@bot.message_handler(commands=["start"])
def start(message):
    user = message.chat.id

    reader, created = Reader.objects.get_or_create(tg_id=user)

    reply_keyboard = take_chapter_keyboard if not reader.taken_juz else finish_reject_kb
    bot.send_message(
        user,
        "Здравствуйте!\nВ этом боте вы можете взять свободную главу из Книги.",
        reply_markup=reply_keyboard,
    )


@bot.message_handler(commands=["help"])
def help(message):
    user = message.chat.id

    help_text = (
        "Доступные команды:\n"
        "/start\n"
        "/help\n"
        "/mystats\n\n"
        "Если вы взяли главу, а клавиатура вдруг не обновилась, отправьте боту сообщение "
        '"Я прочитал главу" (если вы прочитали эту главу) или '
        '"Отказаться от главы" (если вы хотите попробовать взять другую главу)\n\n'
        "Если вы еще не взяли главу, а соответствующая кнопка почему-то не появилась, отправьте боту сообщение "
        '"Взять главу" \n\nЕсли что-то совсем сломалось и не работает — пишите @ruslankhayrut :)'
    )

    bot.send_message(user, help_text)


@bot.message_handler(commands=["mystats"])
def show_stats(message):
    user = message.chat.id
    reader = Reader.objects.get(tg_id=user)
    all_readers = Reader.objects.order_by("-read_counter")

    msg = f"Книг прочитано: *{HCount.objects.get().value}*\n\n"
    msg += create_standings_table(reader, all_readers)
    bot.send_message(user, msg, parse_mode="Markdown")


def take(user):
    not_finished_hatims = Hatim.objects.filter(finished=False)

    keyboard = InlineKeyboardMarkup(row_width=5)

    free_juzes = []
    active_hatim = None
    for hatim in not_finished_hatims:
        this_juzes = Juz.objects.filter(hatim=hatim)
        cant_take = set((juz.number for juz in this_juzes if juz.status in (2, 3)))

        if len(cant_take) < 30:
            free_juzes = sorted(list(set(range(1, 31)).difference(cant_take)))
            active_hatim = hatim
            break

    if not free_juzes:
        active_hatim = Hatim.objects.create()
        free_juzes = range(1, 31)

    keyboard.add(
        *[
            InlineKeyboardButton(juz_n, callback_data=f"take/{juz_n}/{active_hatim.id}")
            for juz_n in free_juzes
        ]
    )
    bot.send_message(user, "Выберите главу", reply_markup=keyboard)


def finish(reader, juz_id):
    finished_juz = Juz.objects.get(pk=juz_id)
    finished_juz.set_status(3)
    msg = "Спасибо!"

    fin = finished_juz.hatim.check_finished()

    if fin:
        counter = HCount.objects.get()
        counter.increment()
        msg += "\nВы дочитали последнюю главу книги. Пожалуйста, прочитайте дополнительные страницы."

    reader.finish_juz()
    bot.send_message(reader.tg_id, msg, reply_markup=take_chapter_keyboard)


def reject(reader, juz_id):
    rej_juz = Juz.objects.get(pk=juz_id)
    rej_juz.set_status(1)

    reader.take_juz(None)

    bot.send_message(reader.tg_id, "Жаль =(", reply_markup=take_chapter_keyboard)


@bot.message_handler(content_types=["text"])
@grab_name
def text_handler(message):
    text = message.text
    user = message.chat.id
    reader = Reader.objects.get(tg_id=user)
    taken_juz = reader.taken_juz

    if text == "Взять главу":
        return take(user)

    if taken_juz and text.startswith("Я прочитал"):
        return finish(reader, taken_juz.id)

    if taken_juz and text == "Отказаться от главы":
        return reject(reader, taken_juz.id)
