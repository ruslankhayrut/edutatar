from . import views
from django.urls import path

app_name = 'schedule'

urlpatterns = [
    path('', views.index, name='index'),
    path('time/', views.time, name='time'),
]