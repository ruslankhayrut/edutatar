from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import *
import json

from .helpers import generate_fake_data, SUBJECTS


def get_homework(student, params):
    resp = {}
    resp_str = 'Вот что вам задали: \n\n'

    subjects = params.get('Subject', [])
    if subjects[0] == 'Все предметы':
        subjects = SUBJECTS

    subject_objs = Subject.objects.filter(name__in=subjects, student=student)
    for s in subject_objs:
        resp_str += '{}: {}\n\n'.format(s.name, s.homework)

    resp.update({'fulfillmentText': resp_str})
    return resp


def get_mark(student, params):
    resp = {}
    resp_str = 'Вот твои оценки:\n\n'

    subjects = params.get('Subject', [])
    if subjects[0] == 'Все предметы':
        subjects = SUBJECTS
        resp_str = 'Вот твои оценки по каждому предмету:\n\n'

    subject_objs = Subject.objects.filter(name__in=subjects, student=student)

    for s in subject_objs:
        resp_str += '{}: {}\n\n'.format(s.name, s.marks_string)

    resp.update({'fulfillmentText': resp_str})
    return resp


def get_avg_mark(student, params):
    resp = {}
    resp_str = 'Вот средний балл:\n\n'

    subjects = params.get('Subject', [])
    if subjects[0] == 'Все предметы':
        subjects = SUBJECTS
        resp_str = 'Вот твои средние оценки по каждому предмету:\n\n'

    subject_objs = Subject.objects.filter(name__in=subjects, student=student)

    for s in subject_objs:
        resp_str += '{}: {}\n\n'.format(s.name, s.average_mark)

    resp.update({'fulfillmentText': resp_str})
    return resp


@csrf_exempt
def index(request):
    json_str = request.body.decode('utf-8')
    request = json.loads(json_str)
    qres = request.get('queryResult')
    params = qres['parameters']
    action = qres.get('action')

    telegram_id = request.get('originalDetectIntentRequest').get('payload').get('data').get('chat').get('id')

    student, created = Student.objects.get_or_create(telegram_id=telegram_id)
    if created:
        generate_fake_data(student)

    handler_func = handlers.get(action)
    webhook_response = handler_func(student, params) if handler_func else {'fulfillmentText': qres['fulfillmentText']}

    return JsonResponse(webhook_response)


handlers = {
    'get_homework': get_homework,
    'get_mark': get_mark,
    'get_avg_mark': get_avg_mark
}
