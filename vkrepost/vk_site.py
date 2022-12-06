import datetime

import requests
from django.conf import settings
from requests.models import Response


class VKImage:
    def __init__(self, url: str = "", width: int = 0, height: int = 0):
        self.photo_url = url
        self.width = width
        self.height = height

    def __bool__(self) -> bool:
        return bool(self.photo_url)


class VKData:
    def __init__(self):
        self.data = None

    @classmethod
    def from_json(cls, data: dict):
        instance = cls()
        instance.data = data
        return instance

    def __build_title_from_post_text(self) -> str:
        text = self.text

        words = [w.strip(' ,;:@"*()') for w in text.split()]
        if not words:
            return ""

        title = " ".join(words[:3]) if len(words) >= 3 else words[0]
        return title

    @property
    def title(self) -> str:
        attachments = self.data["object"].get("attachments", [])
        if attachments and attachments[0]["type"] == "album":
            return attachments[0]["title"]

        return self.__build_title_from_post_text()

    @property
    def lead(self) -> str:
        return self.data["object"]["text"][:100]

    @property
    def text(self) -> str:
        return self.data["object"]["text"]

    @property
    def photo(self) -> VKImage:
        attachments = self.data["object"].get("attachments", [])
        if not attachments:
            return VKImage()

        attachment = attachments[0]
        if attachment["type"] not in ("photo", "album"):
            return VKImage()

        first_photo = attachment["photo"] if attachment["type"] == "photo" else attachment["thumb"]
        first_photo = first_photo["sizes"][-1]

        url = first_photo["url"]
        width = first_photo["width"]
        height = first_photo["height"]
        return VKImage(url, width, height)


class VKAPI:
    @classmethod
    def send_message(cls, user_id: int, text: str) -> Response:
        timestamp = int(datetime.datetime.now().timestamp())

        url = "https://api.vk.com/method/messages.send"
        r = requests.post(
            url,
            params=dict(
                user_id=user_id,
                message=text,
                access_token=settings.VK_TOKEN,
                v=settings.VK_API,
                random_id=timestamp,
            ),
        )
        return r
