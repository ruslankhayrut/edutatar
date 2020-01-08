from django.shortcuts import render, HttpResponseRedirect, reverse, HttpResponse
from django.http import JsonResponse
from django.views import View
from .tasks import exec
from celery import current_app
import os
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
    os.remove(os.path.join(FILES_DIR, file_name))
    return HttpResponse(status=200)

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
        return HttpResponseRedirect(reverse('index'))