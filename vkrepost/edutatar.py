import re
from .remove_emoji import strip_emoji
from .config import LOGIN, PASSWORD
from .eduauth import edu_auth
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
    photo_url = data['photo']['photo_url']
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
