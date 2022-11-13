from django.urls import path

from . import views
from .config import TOKEN

app_name = "vkrepost"
urlpatterns = [
    path("", views.info, name="info"),
    path("callback/{}".format(TOKEN[:6]), views.process, name="process"),
]
