from django.contrib import admin
from .models import *

# Register your models here.
class LessonInline(admin.TabularInline):
    model = Lesson

class BreakInline(admin.TabularInline):
    model = Break

class ScheduleInline(admin.TabularInline):
    model = Schedule

class DayInline(admin.TabularInline):
    model = Day

class ScheduleAdmin(admin.ModelAdmin):
    inlines = [
        LessonInline,
        BreakInline,
    ]


class DayAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'schedule')


class LessonAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'schedule')


class BreakAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'schedule')


admin.site.register(Break, BreakAdmin)
admin.site.register(Lesson, LessonAdmin)
admin.site.register(Schedule, ScheduleAdmin)
admin.site.register(Day, DayAdmin)