import json
from traceback import format_exc

from django.conf import settings
from django.shortcuts import HttpResponse, render
from django.views.decorators.csrf import csrf_exempt

from .eduauth import EdutatarSession
from .edutatar import VKRepostManager
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

        session = EdutatarSession(settings.EDU_LOGIN, settings.EDU_PASSWORD)
        reposter = VKRepostManager(session)

        try:
            result = reposter.post_news(vk_data)
            msg = "Новость успешно отправлена"
            if not result.ok:
                raise RuntimeError(
                    f"Connection error. Status code {result.status_code}"
                )
        except Exception as e:
            msg = f"Во время отправки новости произошла ошибка.\n{e}\n{format_exc()}"

        VKAPI.send_message(settings.VK_OWNER_ID, msg)

        return HttpResponse("OK", status=200)

    return HttpResponse("Bad request", status=400)
