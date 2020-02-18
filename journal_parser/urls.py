from django.urls import path

from . import views

app_name = 'journal_parser'
urlpatterns = [
    path('', views.check_journal, name='check_journal'),
    path('process_journal', views.process, name='process'),
]