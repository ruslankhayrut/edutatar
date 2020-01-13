from django.shortcuts import render
from .config import CONF_STR, API, OWNER_ID, TOKEN
from .edutatar import post_news
import json
import datetime
import time
import requests
# Create your views here.
def info(request):
    return render(request, 'vkrepost/info.html')

def process(request):
    data = json.loads(request.data, encoding='utf-8')

    if data['type'] == 'confirmation':
        return CONF_STR

    elif data['type'] == 'wall_post_new':

        text, photo_url = extract_data(data)

        msg = 'В вашем сообществе новая запись:\n\n{0}\n{1}'.format(text, photo_url)

        send_message(msg)

        return 'ok', execute(text, photo_url)


def execute(text, photo_url):
    d = {}
    d['date'] = datetime.datetime.strftime(datetime.datetime.now(), '%d.%m.%Y')
    d['text'] = text
    d['photo'] = photo_url

    send_message('Отправляем пост в edu.tatar')

    r = post_news(d)
    if r == 200:
        send_message('Новость успешно отправлена!')
    else:
        send_message('Во время отправки произошла ошибка')


def send_message(text):
    url = 'https://api.vk.com/method/messages.send?user_id={0}&message={1}&access_token={2}&v={3}&random_id={4}'.format(
        OWNER_ID, text, TOKEN, API, int(time.time()))
    r = requests.post(url)
    return r


def extract_data(data):
    text = data['object']['text']

    photo_url = ''

    attachments = data['object'].get('attachments')
    if attachments:
        photos = [att for att in attachments if att['type'] == 'photo']
        if photos:
            selected_photo = photos[0]

            selected_size = selected_photo['photo']['sizes'][-1]  # the biggest one

            photo_url = selected_size['url']


    return text, photo_url