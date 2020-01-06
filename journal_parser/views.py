from django.shortcuts import render, HttpResponse, HttpResponseRedirect, reverse
from journal_parser.JournalParser.main import execute

import magic
import os


def index(request):
    return render(request, 'journal_parser/index.html')

def check_journal(request):
    return render(request, 'journal_parser/check.html')


def process(request):

    context = {
        'params': dict(request.POST),
    }

    #return render(request, 'journal_parser/finished.html', context)

    fn = execute(context)
    with open(fn, 'rb') as fd:
        mtype = magic.from_file(fn, True)
        response = HttpResponse(fd, content_type=mtype)
        response['Content-Disposition'] = 'attachment; filename="%s"' %fn
    os.remove(fn)
    return response

def act(request):
    if '_journal' in request.POST:
        return HttpResponseRedirect(reverse('journal_parser:check_journal'))
    elif '_vkrepost' in request.POST:
        return HttpResponseRedirect(reverse('index'))