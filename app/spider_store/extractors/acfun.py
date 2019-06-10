# _*_ coding:utf-8 _*_
import re
from app.spider_store.common import (
    get_content,
)


def acfun_download(url):
    response = get_content(url)
    if re.search(r'data-title="(.*?)"', response, re.S).group(1):
        title = re.search(r'data-title="(.*?)"', response, re.S).group(1)
    elif re.search(r'<title>(.*?)\s-\sAcFun弹幕视频网.*</title>', response, re.S).group(1):
        title = re.search(r'<title>(.*?)\s-\sAcFun弹幕视频网.*</title>', response, re.S).group(1)
    else:
        title = re.search(r'data-proof="(.*?)"', response, re.S).group(1)

    thumbnail_url = re.search(r'"coverImage":"(.*?)"', response).group(1)

    if re.search(r'data-uname="(.*?)"', response, re.S).group(1):
        source = re.search(r'data-uname="(.*?)"', response, re.S).group(1)
    elif re.search(r'"username":"(.*?)"', response, re.S).group(1):
        source = re.search(r'"username":"(.*?)"', response, re.S).group(1)
    else:
        source = re.search(r'data-name="(.*?)"', response, re.S).group(1)

    video_url = None
    type = news_type(url)

    data = {
        "type": type,
        "title": title,
        "source": source,
        "thumbnail_urls": [thumbnail_url],
        "image_urls": None,
        "video_url": video_url,
        "ext": None,
        "size": None,
    }

    return data


def news_type(url):
    if url:
        return "video"


download = acfun_download
