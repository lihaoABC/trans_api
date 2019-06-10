# _*_ codingLUTF-8 _*_
import logging
import random
import urllib.parse
from app.spider_store.common import (
    match1,
    get_content,
)

from app.spider_store.configs import FAKE_USER_AGENT

headers = {
        'user-agent': random.choice(FAKE_USER_AGENT)
    }


def baomihua_download_by_id(_id, title, source, img_url, type):
    html = get_content(
        'http://play.baomihua.com/getvideourl.aspx?flvid={}&devicetype='
        'phone_app'.format(_id)
    )
    host = match1(html, r'host=([^&]*)')
    _type = match1(html, r'videofiletype=([^&]*)')
    vid = match1(html, r'&stream_name=([^&]*)')
    dir_str = match1(html, r'&dir=([^&]*)').strip()
    video_url = 'http://{}/{}/{}.{}'.format(host, dir_str, vid, _type)
    logging.debug("url is {}".format(video_url))
    if title is None:
        title = match1(html, r'&title=([^&]*)')
        title = urllib.parse.unquote(title)
    if source is None:
        return None
    if img_url is None:
        img_url = match1(html, r'&video_img=([^&]*)')

    ext = _type
    size = int(match1(html, r'&videofilesize=([^&]*)'))
    size = float("{:.2f}".format(int(size) / 1024 / 1024))

    data = {
        "type": type,
        "title": title,
        "source": source,
        "thumbnail_urls": [img_url],
        "image_urls": None,
        "video_url": [video_url],
        "ext": ext,
        "size": size,
    }

    return data


def baomihua_download(url):
    html = get_content(url)
    type = news_type(url)
    title = match1(html, r"var\s*temptitle\s*=\s*'(.*?)';")
    source = match1(html, r"var\s*appName\s*=\s*\"(.*?)\";")
    img_url = match1(html, r"var\s*pic\s*=\s*\"(.*?)\";")
    _id = match1(html, r'flvid\s*=\s*(\d+)')
    if type == "video":
        return baomihua_download_by_id(
            _id, title, source, img_url, type,
        )


def news_type(url):
    if url:
        return "video"


download = baomihua_download
