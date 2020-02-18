from django.shortcuts import render, get_object_or_404, get_list_or_404, HttpResponse
from .models import *
import datetime

# Create your views here.
def index(request):
    if request.method == 'GET':
        return render(request, 'schedule/index.html')

    return HttpResponse(status=200)

def time(request):
    if request.method == 'GET':
        n_time = datetime.datetime.now().time()

        context = {
            'time': n_time
        }

        n_weekday = datetime.datetime.now().isoweekday() #1 - 7

        today_day = get_object_or_404(Day, number=n_weekday)
        today_schedule_id = today_day.schedule.id

        today_lessons = get_list_or_404(Lesson, schedule=today_schedule_id)
        for lesson in today_lessons:
            if lesson.start_time <= n_time <= lesson.lesson_end:
                info = {
                    'lesson_num': lesson.number,
                    'lesson_end': lesson.lesson_end,
                }
                context.update({'info': info})
                return render(request, 'schedule/time.html', context)

        today_breaks = get_list_or_404(Break, schedule=today_schedule_id)
        for br in today_breaks:
            if br.start_time <= n_time <= br.break_end:
                info = {
                    'break_end': br.break_end,
                }
                context.update({'info': info})
                return render(request, 'schedule/time.html', context)


        context.update({'alt_message': today_day.alt_message})
        return render(request, 'schedule/time.html', context)
    return HttpResponse(status=200)
