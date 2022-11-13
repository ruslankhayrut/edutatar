from django.conf import settings
from django.urls import path

from . import views

app_name = "vkrepost"
urlpatterns = [
    path("", views.info, name="info"),
    path("callback/{}".format(settings.VK_TOKEN[:6]), views.process, name="process"),
]
