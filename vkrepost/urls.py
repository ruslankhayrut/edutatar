from django.urls import path

from . import views

app_name = 'vkrepost'
urlpatterns = [
    path('', views.info, name='info'),
]