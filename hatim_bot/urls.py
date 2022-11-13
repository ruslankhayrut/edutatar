from django.urls import path

from . import views
from .config import token

app_name = "hatim_bot"
urlpatterns = [
    path(token, views.index, name="index"),
    path("", views.set_webhook, name="set_webhook"),
]
