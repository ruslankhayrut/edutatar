from django.shortcuts import render, HttpResponseRedirect, reverse, HttpResponse
import os
from edutatar.settings import FILES_DIR
from .JournalParser.main import execute
from .JournalParser.params import KEYS


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


def act(request):
    if '_journal' in request.POST:
        return HttpResponseRedirect(reverse('journal_parser:check_journal'))
