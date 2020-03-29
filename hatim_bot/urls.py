from django.urls import path
from .config import token

from . import views

app_name = 'hatim_bot'
urlpatterns = [
    path(token, views.index, name='index'),
    path('', views.set_webhook, name='set_webhook'),
    # path('take', views.take, name='take'),
    # path('reject', views.reject, name='reject'),
    # path('finish', views.finish, name='finish'),
]