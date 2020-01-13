from django.shortcuts import render, HttpResponse
from .config import token, owner_id
import telebot
import requests

bot = telebot.TeleBot(token)

def index(request):
    if request.method == 'POST':
        if request.headers.get('content-type') == 'application/json':
            json_string = request.get_data().decode('utf-8')
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return HttpResponse(status=200)
    else:
        return render(request, 'vosp_bot/index.html')


def set_webhook(request):
    URL1 = 'https://api.telegram.org/bot{}/setWebhook?'.format(token)
    URL2 = 'features.li79.ru/vospbot/{}'.format(token)
    r = requests.post('https://api.telegram.org/bot{}/deleteWebhook'.format(token))
    r = r.json()
    if r['ok']:
        s = requests.post(URL1 + URL2)
        s = s.json()
        if s['ok']:
            bot.send_message(owner_id, 'Webhook was set')
            return '<h1>Bot greets you</h1>'
    return '<h1>Something went wrong</h1>'

@bot.message_handler(content_types=['text'])
def text_handler(message):
    bot.send_message(message.from_user_id, message.text)