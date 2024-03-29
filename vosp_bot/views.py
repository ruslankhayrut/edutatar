import datetime
import locale

import requests
import telebot
from django.shortcuts import HttpResponse, render
from django.views.decorators.csrf import csrf_exempt

from .config import owner_id, token
from .models import Mutfak, Vosp

locale.setlocale(locale.LC_ALL, "ru_RU.UTF-8")

bot = telebot.TeleBot(token, threaded=False)


@csrf_exempt
def index(request):
    if request.method != "POST":
        return HttpResponse(status=403)
    if request.META.get("CONTENT_TYPE") != "application/json":
        return HttpResponse(status=403)

    json_string = request.body.decode("utf-8")
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])

    return render(request, "vosp_bot/index.html")


def set_webhook(request):
    URL1 = "https://api.telegram.org/bot{}/setWebhook?".format(token)
    URL2 = "url=https://features.li79.ru/vospbot/{}".format(token)
    r = requests.post("https://api.telegram.org/bot{}/deleteWebhook".format(token))
    r = r.json()
    if r["ok"]:
        s = requests.post(URL1 + URL2)
        s = s.json()
        if s["ok"]:
            bot.send_message(owner_id, "Webhook was set")
            return HttpResponse("<h1>Bot greets you</h1>")
    return HttpResponse("<h1>Something went wrong</h1>")


def date_to_str(date):
    return datetime.datetime.strftime(date, "%A %d %b")


@bot.message_handler(commands=["lunch"])
def show_lunch_queue(message):
    user = message.chat.id
    if Vosp.objects.get(telegram_id=user):
        queue = Vosp.objects.exclude(lunch_duty_day=None).order_by("lunch_duty_day")
        msg = "Список на ближайшие 10 дней:"
        for v in queue:
            msg += "\n\n*{0}* покупает на ужин в {1}".format(
                v.name, date_to_str(v.lunch_duty_day)
            )
        bot.send_message(user, msg, parse_mode="markdown")

    else:
        bot.send_message(user, "Доступ запрещен")


@bot.message_handler(commands=["evening"])
def show_evening_queue(message):
    user = message.chat.id
    if Vosp.objects.get(telegram_id=user):
        queue = Vosp.objects.exclude(tea_duty_day1=None, tea_duty_day2=None).order_by(
            "tea_duty_day1"
        )
        msg = "Очередь к чаю:"
        for v in queue:
            msg += "\n\n*{0}* покупает в {1} и в {2}".format(
                v.name, date_to_str(v.tea_duty_day1), date_to_str(v.tea_duty_day2)
            )
        bot.send_message(user, msg, parse_mode="markdown")

    else:
        bot.send_message(user, "Доступ запрещен")


@bot.message_handler(commands=["myschedule"])
def show_my_schedule(message):
    user = message.chat.id
    v = Vosp.objects.get(telegram_id=user)
    if v:
        msg = (
            "Вы покупаете на ужин в *{0}*\n\n"
            "Вы покупаете к чаю в *{1}* и в *{2}*".format(
                date_to_str(v.lunch_duty_day),
                date_to_str(v.tea_duty_day1),
                date_to_str(v.tea_duty_day2),
            )
        )
        bot.send_message(user, msg, parse_mode="markdown")
    else:
        bot.send_message(user, "Доступ запрещен")


@bot.message_handler(commands=["mutfak"])
def show_mutfak_schedule(message):
    user = message.chat.id
    if Vosp.objects.get(telegram_id=user):
        queue = Mutfak.objects.all()
        msg = "Примерное расписание дежурств в мутфаке:"
        for m in queue:
            msg += "\n\n*{0}* {1} и {2}".format(
                " ".join(el for el in date_to_str(m.date).split()[1:]), m.vosp1, m.vosp2
            )
        bot.send_message(user, msg, parse_mode="markdown")
    else:
        bot.send_message(user, "Доступ запрещен")


@bot.message_handler(commands=["plus_day"])
def plus_lunch_duty(message):
    user = message.chat.id
    if user == owner_id:
        queue = Vosp.objects.exclude(lunch_duty_day=None).order_by("-lunch_duty_day")
        for vosp in queue:
            vosp.change_day()
            vosp.save()
        bot.send_message(user, "Дежурства перенесены на день вперед")
    else:
        bot.send_message(user, "Вы не можете использовать эту команду")


@bot.message_handler(commands=["minus_day"])
def minus_lunch_duty(message):
    user = message.chat.id
    if user == owner_id:
        queue = Vosp.objects.exclude(lunch_duty_day=None).order_by("-lunch_duty_day")
        for vosp in queue:
            vosp.change_day(val=-1)
            vosp.save()
        bot.send_message(user, "Дежурства перенесены на день назад")
    else:
        bot.send_message(user, "Вы не можете использовать эту команду")


@bot.message_handler(content_types=["text"])
def text_handler(message):
    text = message.text
    if text.lower() == "мой id":
        bot.send_message(message.chat.id, str(message.chat.id))
    else:
        bot.send_message(message.chat.id, message.text)
