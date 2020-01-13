from django.urls import path
from .config import TOKEN
from . import views

app_name = 'vkrepost'
urlpatterns = [
    path('', views.info, name='info'),
    path('callback/{}'.format(TOKEN[:6]), views.process, name='process'),
]