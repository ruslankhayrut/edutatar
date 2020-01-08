from django.urls import path

from . import views

urlpatterns = [
    path('', views.check_journal, name='check_journal'),
    path('process_journal', views.process, name='process'),
    path('task/<str:task_id>/', views.TaskView.as_view(), name='task'),
    path('remove/<str:file_name>/', views.remove, name='remove')
]