from django.shortcuts import render, HttpResponseRedirect, reverse, HttpResponse
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
import os
from edutatar.settings import FILES_DIR
from .JournalParser.main import execute
from .JournalParser.params import KEYS
from django.views.decorators.csrf import csrf_exempt
from .models import Login

def index(request):
    return render(request, 'journal_parser/index.html')

def check_journal(request):
    return render(request, 'journal_parser/check.html')


def process(request):

    context = {key: [None] for key in KEYS}

    context.update(dict(request.POST))

    fn = execute(context)
    path = os.path.join(FILES_DIR, fn)
    with open(path, 'rb') as fd:

        mtype = 'application / vnd.openxmlformats - officedocument.spreadsheetml.sheet'
        response = HttpResponse(fd, content_type=mtype)
        response['Content-Disposition'] = 'attachment; filename="%s"' % fn
    os.remove(path)
    return response

@csrf_exempt
def login_check(request):
    if request.method == 'POST':
        login = int(dict(request.POST).get('login', '1'))
        try:
            l = Login.objects.get(login_int=login)
            return JsonResponse({"status": True})
        except ObjectDoesNotExist:
            return JsonResponse({"status": False})






def act(request):
    if '_journal' in request.POST:
        return HttpResponseRedirect(reverse('journal_parser:check_journal'))
