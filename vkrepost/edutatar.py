import re
import os.path
from remove_emoji import strip_emoji
from config import LOGIN, PASSWORD
from eduauth import edu_auth
from gmail_api import gmail_attachments
from bs4 import BeautifulSoup


def upload_img(session, photo_url):
    h = {"Referer": "https://edu.tatar.ru/upload_crop/show/?aspect_ratio=1&index=1&type=2&img_file=",
         }
    img = session.get(photo_url)

    file = {"inpUplCrop1": img.content}

    f = session.post("https://edu.tatar.ru/upload_crop", headers=h, files=file, data={
        'type': 2,
        'aspect_ratio': 1
    })

    return f.text


def process_text(text):
    words = [w.strip(' ,;:@"*()') for w in text.split()]
    sentences = re.split('[.?!]', text)
    try:
        title = words[0] + " " + words[1]
    except IndexError:
        title = words[0]

    if sentences[0] != text:
        lead = sentences[0] + "..."
    else:
        lead = None

    return title, lead


def post_news(data):
    text = strip_emoji(data['text'])

    date = data['date']
    photo_url = data['photo'].get('photo_url')
    title = data['title']

    if not title:
        title, lead = process_text(text)
    else:
        lead = process_text(text)[1]

    session = edu_auth(LOGIN, PASSWORD)

    session.get('https://edu.tatar.ru')
    r = session.get('https://edu.tatar.ru/admin/page/news_block')

    html = BeautifulSoup(r.text, 'html.parser')

    table = html.find_all('table')[0]
    news_block = table.findAllNext('tr')[1]
    link = news_block.find('a', href=True, text='Новости...')['href']
    block_id = re.findall(r'\d+', link)[0]

    session.headers.update({"Host": "edu.tatar.ru",
                            "Origin": "https://edu.tatar.ru",
                            "User-Agent": "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) \
                                            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 \
                                            YaBrowser/18.10.1.382 (beta) Yowser/2.5 Safari/537.36"
                            })

    if photo_url:
        upload_img(session, photo_url)
        width = data['photo']['width']
        height = data['photo']['height']

        h = 145 * int(width / 220)
        w = 220 * int(height / 145)
        if height >= h:
            crop = '0|0|{0}|{1}|{0}|{1}'.format(width, h)
        elif width >= w:
            crop = '0|0|{0}|{1}|{0}|{1}'.format(w, height)
        else:
            crop = '0|0|220|145|220|145'

    else:
        crop = None

    h = {"Referer": "https://edu.tatar.ru/admin/page/news/edit?news_block_id={}".format(block_id),
         "Content-Type": "application/x-www-form-urlencoded"}

    r = session.post('https://edu.tatar.ru/admin/page/news/edit?news_block_id={}'.format(block_id), headers=h,
                     data={
                         'news[title]': title,
                         'news[ndate]': date,
                         'news[source]': None,
                         'news[lead]': lead,
                         'news[text]': '<p> {} </p>'.format(text),
                         'news[imgUCAdjData1]': crop,
                         'news[image_idx]': 1,
                         'news[gallery_id]': None,
                         'news[videoteka_id]': None,
                         'news[trans_school]': 0,
                         'news[trans_region]': 0,
                         'news[trans_global]': 0,
                     }
                     )
    return r.status_code


def post_page(data):
    # TODO Сделать обновление страницы ежедневного меню
    session = edu_auth(LOGIN, PASSWORD)
    session.get('https://edu.tatar.ru')
    page_id = 800107
    url = f'https://edu.tatar.ru/admin/page/simple_page/edit/{page_id}'
    h = {"Referer": url,
         "Content-Type": "application/x-www-form-urlencoded"}
    r = session.get(url)
    html = BeautifulSoup(r.text, 'html.parser')
    one_link = f'<p><a href="/upload/storage/org1505/files/food/{data["filename"]}">{data["filename"]}</a></p>'
    text = one_link + str(html.find_all('textarea', id='simple_page_data')[-1].contents[-1])
    r = session.post(url=url, headers=h,
                     data={'simple_page[title]': 'Ежедневные Меню',
                           'simple_page[description]': '',
                           'simple_page[data]': text,
                           'simple_page[organization_id]': 1505}
                     )
    print(r)


def get_files(session, from_folder='food'):
    url = "https://edu.tatar.ru/js/ckfinder/core/connector/php/connector.php"
    params = {'command': 'GetFiles',
              'type': 'Files',
              'currentFolder': f'/{from_folder}/',
              # 'hash': 'cc921cf4d95e67d0',
              # 'showThumbs': 1,
              # 'langCode': 'ru'
              }
    res = session.get(url, params=params)
    from xml.etree import ElementTree
    tree = ElementTree.fromstring(res.content)
    print(tree)
    return res


def upload_file(session, file_path, target_folder):
    data = {}
    img = open(file_path, mode='rb')
    filename = img.name.split('\\')[-1]
    data[filename] = img
    f = upload_files(session, data, target_folder)
    img.close()
    return f.text


def upload_files(session, files, target_folder='food'):
    h = {"Referer": "https://edu.tatar.ru/",
         }
    # url = "https://edu.tatar.ru/upload/storage/org1505/files/" + target_folder + '/'
    # url = "https://edu.tatar.ru/js/ckfinder/core/connector/php/connector.php?command=FileUpload&type=Files&currentFolder=/food/&hash=cc921cf4d95e67d0&langCode=ru"
    url = f"https://edu.tatar.ru/js/ckfinder/core/connector/php/connector.php"
    params = {'command': 'FileUpload',
              'type': 'Files',
              'currentFolder': f"/{target_folder}/",
              # 'hash': 'cc921cf4d95e67d0', # эти параметрыо казались не обязательными... вроде
              # 'langCode': 'ru'
              }
    f = session.post(url=url,
                     headers=h,
                     params=params,
                     files=files)
    return f


def upload_multiple_files(session, files_list):
    for filename in files_list:
        print(upload_file(session, filename, 'food'))


def upload_menus(session):
    list_of_filenames = []
    for i in range(1, 31):
        day = str(i // 10) + str(i % 10)
        filename = f'D:\\Downloads\\2021-09-{day}-sm.xlsx'
        if os.path.exists(filename):
            list_of_filenames.append(filename)

    upload_multiple_files(session, list_of_filenames)


def daily_menu():
    g_session = gmail_attachments.connect()
    edu_session = edu_auth(LOGIN, PASSWORD)

    data = gmail_attachments.get_attachments(g_session, {'labels': ['Label_7', 'UNREAD']})
    # files = {}
    for mail_id, attach in data.items():
        files = attach.items()
        upload_files(edu_session, files)
        gmail_attachments.label_modify(g_session, 'me', mail_id, ['UNREAD'])


if __name__ == '__main__':
    post_page({'filename': 'hello.xls'})
