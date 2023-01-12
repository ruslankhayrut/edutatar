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
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.static import serve as mediaserve

urlpatterns = [
    path("admin/", admin.site.urls),
    path("vkrepost/", include("vkrepost.urls")),
    path("vospbot/", include("vosp_bot.urls")),
    path("schedule/", include("schedule.urls")),
    path("sharebot/", include("hatim_bot.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    urlpatterns += [
        url(
            f'^{settings.MEDIA_URL.lstrip("/")}(?P<path>.*)$',
            mediaserve,
            {"document_root": settings.MEDIA_ROOT},
        ),
        url(
            f'^{settings.STATIC_URL.lstrip("/")}(?P<path>.*)$',
            mediaserve,
            {"document_root": settings.STATIC_ROOT},
        ),
    ]
