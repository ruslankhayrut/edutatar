from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .config import CONF_STR
from .edutatar import post_news
import datetime
import json


def info(request):
    return render(request, 'vkrepost/info.html')


@csrf_exempt
def process(request):
    if request.method != "POST":
        return HttpResponse("Forbidden", status=403)

    data = request.body.decode('utf-8')
    data = json.loads(data)

    if data.get('type') == 'confirmation':
        return HttpResponse(CONF_STR)

    elif data.get('type') == 'wall_post_new':
        proc(data)
        return HttpResponse('ok', status=200)

    return HttpResponse('undefined data')


def proc(data):
    text, photo_data, title = extract_data(data)

    return execute(title, text, photo_data)


def execute(title, text, photo_data):
    d = {}
    d['date'] = datetime.datetime.strftime(datetime.datetime.now(), '%d.%m.%Y')
    d['text'] = text
    d['photo'] = photo_data
    d['title'] = title

    post_news(d)


def extract_data(data):
    text = data['object']['text']

    title = ''
    photo_data = {}

    attachments = data['object'].get('attachments')
    if not attachments:
        return [], [], ""

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