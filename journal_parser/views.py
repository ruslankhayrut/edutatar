from django.shortcuts import render, HttpResponseRedirect, reverse, HttpResponse
import os
from edutatar.settings import FILES_DIR
from .JournalParser.main import execute
from .JournalParser.params import KEYS
from django.views.decorators.csrf import csrf_exempt


#TODO: remove trial view etc
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
def form(request):
    if request.method == 'POST':
        data = dict(request.POST)
        vls = []
        for key, val in data.items():
            if not val[0]:
                vls.append(key)
        if vls:
            context = {'values': vls}
            return render(request, 'journal_parser/failure.html', context)
        return render(request, 'journal_parser/success.html')

    else:
        return render(request, 'journal_parser/form.html')

def act(request):
    if '_journal' in request.POST:
        return HttpResponseRedirect(reverse('journal_parser:check_journal'))
