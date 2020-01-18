from django.urls import path
from .config import token

from . import views

app_name = 'vosp_bot'
urlpatterns = [
    path(token, views.index, name='index'),
    path('', views.set_webhook, name='set_webhook'),
]