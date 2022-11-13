import os.path
import re
from xml.etree import ElementTree

from bs4 import BeautifulSoup
from django.conf import settings
from requests_toolbelt import MultipartEncoder

from vkrepost.eduauth import EdutatarSession
from vkrepost.remove_emoji import strip_emoji


def upload_img(session, photo_url):
    h = {
        "Referer": "https://edu.tatar.ru/upload_crop/show/?aspect_ratio=1&index=1&type=2&img_file=",
    }
    img = session.get(photo_url)

    file = {"inpUplCrop1": img.content}

    f = session.post(
        "https://edu.tatar.ru/upload_crop",
        headers=h,
        files=file,
        data={"type": 2, "aspect_ratio": 1},
    )

    return f.text


def post_news(data):
    text = strip_emoji(data["text"])

    date = data["date"]
    photo_url = data["photo"].get("photo_url")
    title = data["title"]
    boundary = "my-shiny-boundary"

    if not title:
        title, lead = process_text(text)
    else:
        lead = process_text(text)[1]

    session = edu_auth(settings.EDU_LOGIN, settings.EDU_PASSWORD)

    session.get("https://edu.tatar.ru")
    r = session.get("https://edu.tatar.ru/admin/page/news_block")

    html = BeautifulSoup(r.text, "html.parser")

    table = html.find_all("table")[0]
    news_block = table.findAllNext("tr")[1]
    link = news_block.find("a", href=True, text="Новости...")["href"]
    block_id = re.findall(r"\d+", link)[0]

    session.headers.update(
        {
            "Host": "edu.tatar.ru",
            "Origin": "https://edu.tatar.ru",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
                            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 \
                            Safari/537.36 OPR/92.0.0.0",
        }
    )

    if photo_url:
        upload_img(session, photo_url)
        width = data["photo"]["width"]
        height = data["photo"]["height"]

        h = 145 * int(width / 220)
        w = 220 * int(height / 145)
        if height >= h:
            crop = "0|0|{0}|{1}|{0}|{1}".format(width, h)
        elif width >= w:
            crop = "0|0|{0}|{1}|{0}|{1}".format(w, height)
        else:
            crop = "0|0|220|145|220|145"

    else:
        crop = None

    h = {
        "Referer": f"https://edu.tatar.ru/admin/page/news/edit?news_block_id={block_id}",
        "Content-Type": f"multipart/form-data; boundary={boundary}",
    }

    files = MultipartEncoder(
        {
            "news[title]": (None, title),
            "news[ndate]": (None, date),
            "news[source]": (None, ""),
            "news[lead]": (None, f"<p> {lead} </p>"),
            "news[text]": (None, f"<p> {text} </p>"),
            "news[imgUCAdjData1]": (None, crop),
            "news[image_idx]": (None, "1"),
            "news[gallery_id]": (None, ""),
            "news[videoteka_id]": (None, ""),
            "news[trans_school]": (None, "0"),
            "news[trans_region]": (None, "0"),
            "news[trans_global]": (None, "0"),
        },
        boundary=boundary,
    )

    r = session.post(
        f"https://edu.tatar.ru/admin/page/news/edit?news_block_id={block_id}",
        headers=h,
        data=files.to_string(),
    )

    return r


def post_page(session, page_id, data):
    session.get("https://edu.tatar.ru")
    url = f"https://edu.tatar.ru/admin/page/simple_page/edit/{page_id}"
    h = {"Referer": url, "Content-Type": "application/x-www-form-urlencoded"}

    file_links = ""
    for file in data:
        file_links = (
            f'<p><a href="/upload/storage/org1505/files/food/{file[0]}">{file[0]}</a></p>\n'
            + file_links
        )
    text = file_links
    session.post(
        url=url,
        headers=h,
        data={
            "simple_page[title]": "Ежедневные Меню",
            "simple_page[description]": "",
            "simple_page[data]": text,
            "simple_page[organization_id]": 1505,
        },
    )


def get_files(session, from_folder="food"):
    url = "https://edu.tatar.ru/js/ckfinder/core/connector/php/connector.php"
    params = {
        "command": "GetFiles",
        "type": "Files",
        "currentFolder": f"/{from_folder}/",
    }
    res = session.get(url, params=params)
    files = ElementTree.fromstring(res.content).findall("Files")[0].findall("File")
    files_list = []
    for file in files:
        filename = file.get("name")
        files_list.append(
            (
                filename,
                "/".join(
                    [
                        "https://edu.tatar.ru/upload/storage/org1505/files",
                        from_folder,
                        filename,
                    ]
                ),
            )
        )
    return files_list


def upload_file(session, file_path, target_folder):
    data = {}
    img = open(file_path, mode="rb")
    filename = img.name.split("\\")[-1]
    data[filename] = img
    f = upload_files(session, data, target_folder)
    img.close()
    return f


def upload_files(session, files, target_folder="food"):
    h = {
        "Referer": "https://edu.tatar.ru/",
    }
    url = "https://edu.tatar.ru/js/ckfinder/core/connector/php/connector.php"
    params = {
        "command": "FileUpload",
        "type": "Files",
        "currentFolder": f"/{target_folder}/",
    }
    f = []
    for file in files:
        f.append(session.post(url=url, headers=h, params=params, files=[file]))

    return f


def upload_multiple_files(session, files_list):
    for filename in files_list:
        print(upload_file(session, filename, "food"))


def upload_menus(session):
    list_of_filenames = []
    for i in range(1, 31):
        day = str(i // 10) + str(i % 10)
        filename = f"D:\\Downloads\\2021-09-{day}-sm.xlsx"
        if os.path.exists(filename):
            list_of_filenames.append(filename)

    upload_multiple_files(session, list_of_filenames)


# def daily_menu():
#     g_session = gmail_attachments.connect(proxy=PROXY)
#     edu_session = edu_auth(LOGIN, PASSWORD, PROXY)
#     data = gmail_attachments.get_attachments(
#         g_session, {"labels": ["Label_7", "UNREAD"]}
#     )
#     for mail_id, attach in data.items():
#         files = normalize_filenames(attach).items()
#         upload_files(edu_session, files)
#         post_page(edu_session, page_id=800107, data=get_files(edu_session))
#         gmail_attachments.label_modify(
#             g_session, "me", mail_id, labels_to_remove=["UNREAD"]
#         )


def normalize_filenames(files_dict):
    res = {}
    for key in files_dict.keys():
        new_key = key[: key.find("sm") + 2] + key[key.find(".") :]
        res[new_key] = files_dict[key]
    return res


if __name__ == "__main__":
    pass
    # daily_menu()
