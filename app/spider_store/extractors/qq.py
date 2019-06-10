# _*_ coding:utf-8 _*_
import re
import json
from app.spider_store.common import (
    get_content,
)


def qq_video_download(url):
    type = "video"
    video_url = None

    if re.search(r"new\.qq\.com/omv/video/", url):
        vid = re.search(r"^http[s]?://new\.qq\.com/omv/video/(.*?)$", url).group(1)
        detail_url = "{}{}".format(
            "https://pacaio.match.qq.com/vlike/detail?vid=",
            vid,
        )
        response = get_content(detail_url)
        info = json.loads(response)
        title = info.get("data").get("title")
        source = info.get("data").get("source")
        if (source is None) or (source == ''):
            source = "腾讯视频"
        if info.get("data").get("imgs").get("228X128"):
            thumbnail_url = info.get("data").get("imgs").get("228X128")
        elif info.get("data").get("imgs").get("496X280"):
            thumbnail_url = info.get("data").get("imgs").get("496X280")
        else:
            thumbnail_url = info.get("data").get("img")

    elif re.search(r"v\.qq\.com/x/page/", url) or re.search(r"v\.qq\.com/x/cover", url):
        response = get_content(url)
        title = re.search(r"<title>(.*?)</title>", response).group(1)
        if (title is None) or (title == ""):
            title = re.search(
                r'<meta\s*itemprop=[\'|"]name[\'|"]\s*name=[\'|"]title[\'|"]\s*content=[\'|"](.*?)[\'|"]>',
                response
            ).group(1)
            if (title is None) or (title == ""):
                title = re.search(
                    r'<meta\s*name=[\'|"]twitter:title[\'|"]\s*property=[\'|"]og:title[\'|"]'
                    r'\s*content=[\'|"](.*?)[\'|"]\s*/>',
                    response
                ).group(1)
        title = re.sub(r"_.*$", '', title)
        try:
            source = re.search(r'<span\s*class=[\'|"]user_name[\'|"]>(.*?)</span>', response).group(1)
        except AttributeError:
            source = re.search(r'<strong\s*class=[\'|"]player_title[\'|"]>(.*?)</strong>', response).group(1)
        
        if (source is None) or (source == ''):
            source = "腾讯视频"

        thumbnail_url = re.search(
            r'<meta\s*itemprop=[\'|"]image[\'|"]\s*content=[\'|"](.*?)[\'|"]>',
            response
        ).group(1)
        if thumbnail_url is None:
            thumbnail_url = re.search(
                r'<meta\s*itemprop=[\'|"]thumbnailUrl[\'|"]\s*content=[\'|"](.*?)[\'|"]>',
                response
            ).group(1)
        if not re.search(r"^http[s]?:(.*)?$", thumbnail_url).group(1):
            thumbnail_url = re.search(
                r'[\'|"]pic_640_360[\'|"]:[\'|"](.*?)[\'|"],',
                response
            ).group(1)

    elif re.search(r"sports\.qq\.com", url):
        return {"message": "腾讯独家，暂不支持"}

    else:
        title = None
        source = None
        thumbnail_url = None
        video_url = None

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


def qq_news_download(url):
    assert url
    return {"message": "暂未开发"}


def qq_spider(url):
    if news_type(url) == "video":
        return qq_video_download(url)
    else:
        return qq_news_download(url)


def news_type(url):

    if "new.qq.com/omv/video/" in url:
        return "video"
    elif "v.qq.com/x/page/" or "v.qq.com/x/cover" in url:
        return "video"
    elif "sports.qq.com" in url:
        return "video"
    else:
        return "news"


download = qq_spider


if __name__ == '__main__':
    # url = 'https://new.qq.com/omv/video/t00306ri7q2'
    url = 'https://v.qq.com/x/cover/rf5im7exssprw0m.html'
    # url = 'https://v.qq.com/x/page/c0867ubrzpl.html'
    # url = 'https://v.sports.qq.com/#/cover/fny2d400zzywx8h/q0030k2jyqf'
    # url = 'https://v.qq.com/x/cover/k4mutekomtrdbux/g0027f3npxu.html'
    data = download(url)
    print(data)