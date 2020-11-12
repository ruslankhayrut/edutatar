from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import *
import json
from functools import wraps

from .helpers import generate_fake_data, SUBJECTS


def get_student(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        telegram_id = request.get('originalDetectIntentRequest').get('payload').get('data').get('chat').get('id')
        student, created = Student.objects.get_or_create(telegram_id=telegram_id)
        if created:
            generate_fake_data(student)
        return func(request, student, *args, **kwargs)
    return wrapper

@get_student
def get_homework(request, student):
    resp = {}
    resp_str = 'Вот что вам задали: \n\n'
    params = request['queryResult']['parameters']

    subjects = params.get('Subject', [])
    if subjects[0] == 'Все предметы':
        subjects = SUBJECTS

    subject_objs = Subject.objects.filter(name__in=subjects, student=student)
    for s in subject_objs:
        hw = s.homework
        resp_str += f'{s.name}: {hw}\n\n'

    resp.update({'fulfillmentText': resp_str})
    return resp

@get_student
def get_mark(request, student):
    resp = {}
    resp_str = 'Вот твои оценки:\n\n'
    params = request['queryResult']['parameters']

    subjects = params.get('Subject', [])
    if subjects[0] == 'Все предметы':
        subjects = SUBJECTS
        resp_str = 'Вот твои оценки по каждому предмету:\n\n'

    subject_objs = Subject.objects.filter(name__in=subjects, student=student)

    for s in subject_objs:
        resp_str += f'{s.name}: {s.marks_string}\n\n'

    resp.update({'fulfillmentText': resp_str})
    return resp

@get_student
def get_avg_mark(request, student):
    resp = {}
    resp_str = 'Вот средний балл:\n\n'
    params = request['queryResult']['parameters']

    subjects = params.get('Subject', [])
    if subjects[0] == 'Все предметы':
        subjects = SUBJECTS
        resp_str = 'Вот твои средние оценки по каждому предмету:\n\n'

    subject_objs = Subject.objects.filter(name__in=subjects, student=student)

    for s in subject_objs:
        resp_str += f'{s.name}: {s.average_mark}\n\n'

    resp.update({'fulfillmentText': resp_str})
    return resp


@csrf_exempt
def index(request):
    request = json.loads(request.body)
    qres = request.get('queryResult')
    action = qres.get('action')
    handler_func = handlers.get(action)
    webhook_response = handler_func(request) if handler_func else {'fulfillmentText': qres['fulfillmentText']}

    return JsonResponse(webhook_response)


handlers = {
    'get_homework': get_homework,
    'get_mark': get_mark,
    'get_avg_mark': get_avg_mark
}

