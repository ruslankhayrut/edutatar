import time
import requests
import json
from django.test import TestCase
from config import *
# Create your tests here.
from vkrepost.views import proc

data = {
    "group_id": 216686905,
    "type": "wall_post_new",
    "event_id": "3f9ad940222414d93e9302207a2f6659c941cf20",
    "v": "5.103",
    "object": {
        "id": 28,
        "from_id": -216686905,
        "owner_id": -216686905,
        "date": 1668242750,
        "marked_as_ads": 0,
        "can_delete": 1,
        "is_favorite": False,
        "post_type": "post",
        "text": "Пост через \"Что у вас нового?\". Без картинок и смайлов. Сразу нажимаю опубликовать",
        "can_edit": 1,
        "created_by": 535463094,
        "comments": {
            "count": 0
        },
        "zoom_text": True,
        "hash": "UVtxbB0-nX8zw7nJuxFxS31c667c"
    }
}
# data = json.loads(data)
if __name__ == '__main__':
    print(proc(data))
