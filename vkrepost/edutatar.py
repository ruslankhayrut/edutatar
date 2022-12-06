import datetime
import re

from bs4 import BeautifulSoup
from requests.models import Response
from requests_toolbelt import MultipartEncoder

from vkrepost.eduauth import EdutatarSession
from vkrepost.helpers import remove_emoji_from_text
from vkrepost.vk_site import VKData, VKImage


class VKRepostManager:
    def __init__(self, session: EdutatarSession):
        self.session = session
        self.boundary = "--my-shiny-boundary"

    def _upload_image(self, image: VKImage) -> str:
        if not image:
            return ""

        h = {
            "Referer": "https://edu.tatar.ru/upload_crop/show/?aspect_ratio=1&index=1&type=2&img_file="
        }
        img = self.session.get(image.photo_url)
        file = {"inpUplCrop1": img.content}

        self.session.post(
            "https://edu.tatar.ru/upload_crop",
            headers=h,
            files=file,
            data={"type": 2, "aspect_ratio": 1},
        )

        width, height = image.width, image.height

        h = 145 * int(width / 220)
        w = 220 * int(height / 145)
        if height >= h:
            crop = f"0|0|{width}|{h}|{width}|{h}"
        elif width >= w:
            crop = f"0|0|{w}|{height}|{w}|{height}"
        else:
            crop = "0|0|220|145|220|145"
        return crop

    def _get_block_id(self) -> str:
        self.session.get("https://edu.tatar.ru")
        r = self.session.get("https://edu.tatar.ru/admin/page/news_block")

        html = BeautifulSoup(r.text, "html.parser")

        table = html.find_all("table")[0]
        news_block = table.findAllNext("tr")[1]
        link = news_block.find("a", href=True, text="Новости...")["href"]
        block_id = re.findall(r"\d+", link)[0]
        return block_id

    def post_news(self, data: VKData) -> Response:
        text = remove_emoji_from_text(data.text)
        date = datetime.date.today().strftime("%d.%m.%Y")

        self.session.login()
        block_id = self._get_block_id()

        crop = self._upload_image(data.photo)

        h = {
            "Referer": f"https://edu.tatar.ru/admin/page/news/edit?news_block_id={block_id}",
            "Content-Type": f"multipart/form-data; boundary={self.boundary}",
        }

        files = MultipartEncoder(
            {
                "news[title]": (None, data.title),
                "news[ndate]": (None, date),
                "news[source]": (None, ""),
                "news[lead]": (None, f"{data.lead}"),
                "news[text]": (None, f"{text}"),
                "news[imgUCAdjData1]": (None, crop),
                "news[image_idx]": (None, "1"),
                "news[gallery_id]": (None, ""),
                "news[videoteka_id]": (None, ""),
                "news[trans_school]": (None, "0"),
                "news[trans_region]": (None, "0"),
                "news[trans_global]": (None, "0"),
            },
            boundary=self.boundary,
        )

        r = self.session.post(
            f"https://edu.tatar.ru/admin/page/news/edit?news_block_id={block_id}",
            headers=h,
            data=files.to_string(),
        )

        return r


if __name__ == "__main__":
    pass
