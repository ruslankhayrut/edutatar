from django.contrib import admin
from .models import *
# Register your models here.

def make_unread(modeladmin, request, queryset):
    queryset.update(status=1)
    hatim = queryset[0].hatim
    hatim.finished = False
    hatim.save()

make_unread.short_description = 'Сделать свободными'

class JuzAdmin(admin.ModelAdmin):
    actions = [make_unread]
    list_display = ('hatim', 'number', 'status', 'reader')
    list_filter = ('hatim', )

class JuzInline(admin.TabularInline):

    model = Juz

class HatimAdmin(admin.ModelAdmin):

    inlines = [JuzInline]

    list_display = ('__str__', 'finished', )

class CounterAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'value')

admin.site.register(Hatim, HatimAdmin)
admin.site.register(Juz, JuzAdmin)
admin.site.register(Reader)
admin.site.register(HCount, CounterAdmin)