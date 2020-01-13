from django.shortcuts import render, HttpResponseRedirect, reverse, HttpResponse
from django.http import JsonResponse
from django.views import View
from .tasks import exec
from celery import current_app
from edutatar.celery import app
import os
import time
from edutatar.settings import FILES_DIR

def index(request):
    return render(request, 'journal_parser/index.html')

def check_journal(request):
    return render(request, 'journal_parser/check.html')


def process(request):

    context = {
        'params': dict(request.POST),
    }

    task = exec.delay(context)

    c = {
        'task_id': task.id,
        'task_status': task.status
    }

    return render(request, 'journal_parser/finished.html', c)

def remove(request, file_name):
    time.sleep(5)
    os.remove(os.path.join(FILES_DIR, file_name))
    return HttpResponse(status=200)

def cancel(request, task_id):
    app.control.revoke(task_id, terminate=True)

    return HttpResponseRedirect(reverse('journal_parser:check_journal'))

class TaskView(View):
    def get(self, request, task_id):
        task = current_app.AsyncResult(task_id)
        response_data = {'task_status': task.status, 'task_id': task.id}
        if task.status == 'SUCCESS':
            response_data['results'] = task.get()
        return JsonResponse(response_data)

def act(request):
    if '_journal' in request.POST:
        return HttpResponseRedirect(reverse('journal_parser:check_journal'))
    elif '_vkrepost' in request.POST:
        return HttpResponseRedirect(reverse('vkrepost:info'))
