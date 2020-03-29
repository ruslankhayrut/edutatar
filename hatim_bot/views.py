from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .config import token, owner_id

import telebot
import requests
import datetime
import time


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

@bot.message_handler(content_types=['text'])
def text_handler(message):
    text = message.text
    if text.lower() == 'мой id':
        bot.send_message(message.chat.id, str(message.chat.id))
    else:
        bot.send_message(message.chat.id, message.text)