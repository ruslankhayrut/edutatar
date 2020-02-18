"""edutatar URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from journal_parser.views import index, act
# from django.views.defaults import server_error
# from functools import partial

#handler500 = partial(server_error, template_name='journal_parser/500.html')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('journal/', include('journal_parser.urls')),
    path('vkrepost/', include('vkrepost.urls')),
    path('vospbot/', include('vosp_bot.urls')),
    path('schedule/', include('schedule.urls')),
    path('', index, name='index'),
    path('act', act, name='act'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

