import json

from django.conf import settings
from django.shortcuts import HttpResponse, render
from django.views.decorators.csrf import csrf_exempt

from .edutatar import post_news
from .vk_site import VKAPI, VKData


def info(request):
    return render(request, "vkrepost/info.html")


@csrf_exempt
def process(request):
    if request.method == "GET":
        return HttpResponse("OK", status=200)

    data = request.body.decode("utf-8")
    data = json.loads(data)
    if data.get("type") == "confirmation":
        return HttpResponse(settings.VK_CONF_STR)

    if data.get("type") == "wall_post_new":
        vk_data = VKData.from_json(data)
        result = post_news(vk_data)

        msg = (
            "Новость успешно отправлена"
            if result.ok
            else "Во время отправки новости произошла ошибка"
        )
        VKAPI.send_message(settings.VK_OWNER_ID, msg)

        return HttpResponse("OK", status=200)

    return HttpResponse("Bad request", status=400)
