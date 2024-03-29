from django.http import HttpRequest
from django.shortcuts import HttpResponse, render
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.http import require_http_methods

from .models import *


# Create your views here.
def model_to_dict(obj, exclude=()):
    d = {}
    for key, val in obj.__dict__.items():
        if key not in (exclude, "_state"):
            if not isinstance(val, datetime.time):
                d[key] = val
            else:
                d[key] = "{}:{}".format(val.hour, val.minute)
    return d


@require_http_methods(["GET"])
@xframe_options_exempt
def index(request: HttpRequest) -> HttpResponse:
    d_number = datetime.datetime.now().isoweekday()

    this_day = Day.objects.get(number=d_number)
    today_schedule = this_day.schedule.id
    alt_message = this_day.alt_message

    today_lessons = Lesson.objects.filter(schedule=today_schedule)
    today_breaks = Break.objects.filter(schedule=today_schedule)

    lessons = [
        model_to_dict(lesson, exclude=("id", "schedule")) for lesson in today_lessons
    ]
    breaks = [model_to_dict(br, exclude="id") for br in today_breaks]

    data = {"lessons": lessons, "breaks": breaks, "alt_message": alt_message}

    return render(request, "schedule/index.html", data)
