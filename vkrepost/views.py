from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .config import CONF_STR, API, OWNER_ID, TOKEN
from .edutatar import post_news
import datetime
import time
import requests
import json


def info(request):
    return render(request, 'vkrepost/info.html')

@csrf_exempt
def process(request):
    if request.method == 'POST':
        data = request.body.decode('utf-8')
        data = json.loads(data)
        if data.get('type') == 'confirmation':
            return HttpResponse(CONF_STR)

        elif data.get('type') == 'wall_post_new':
            proc(data)
            return HttpResponse('ok', status=200)

        return HttpResponse('undefined data')

    return HttpResponse('ok')


def proc(data):
    text, photo_data, title = extract_data(data)
    
    return execute(title, text, photo_data)

def execute(title, text, photo_data):
    d = {}
    d['date'] = datetime.datetime.strftime(datetime.datetime.now(), '%d.%m.%Y')
    d['text'] = text
    d['photo'] = photo_data
    d['title'] = title


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
    title = ''
    photo_data = {}

    attachments = data['object'].get('attachments')
    if attachments:
        photos = []
        album = None
        for att in attachments:
            if att['type'] == 'photo':
                photos.append(att)
            elif att['type'] == 'album':
                album = att['album']

        if photos:
            selected_photo = photos[0]

            selected_size = selected_photo['photo']['sizes'][-1]  # the biggest one

            photo_data['photo_url'] = selected_size['url']

            photo_data['width'] = selected_size['width']
            photo_data['height'] = selected_size['height']

        elif album:
            selected_size = album['thumb']['sizes'][-1]
            photo_data['photo_url'] = selected_size['url']

            photo_data['width'] = selected_size['width']
            photo_data['height'] = selected_size['height']
            title = album['title']




    return text, photo_data, title