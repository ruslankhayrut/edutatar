from django.urls import path
from .config import token

from . import views

app_name = 'mufteam_bot'
urlpatterns = [
    path(token, views.index, name='index'),
]