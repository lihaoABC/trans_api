# _*_ coding:utf-8 _*_
import re
from app.spider_store.common import (
    get_content,
)

fake_headers_mobile = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'UTF-8,*;q=0.5',
    'Accept-Encoding': 'gzip,deflate,sdch',
    'Accept-Language': 'en-US,en;q=0.8',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 4.4.2; Nexus 4 Build/KOT49H) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.114 Mobile Safari/537.36'
}


def miaopai_download(url):
    mobile_page = get_content(url, headers=fake_headers_mobile)
    try:
        title = re.search(r'([\'"])title\1:\s*([\'"])(.+?)\2,', mobile_page).group(3)
    except:
        title = re.search(r'([\'"])status_title\1:\s*([\'"])(.+?)\2,', mobile_page).group(3)
    title = title.replace('\n', '_')
    source = re.search(r'([\'"])screen_name\1:\s*([\'"])(.+?)\2,', mobile_page).group(3)
    stream_url = re.search(r'([\'"])stream_url\1:\s*([\'"])(.+?)\2,', mobile_page).group(3)
    thumbnail_urls = re.search(
        r'[\'"]page_pic[\'"]:[\s\W\S\w]*[\'"]url[\'"]:\s*[\'"](.*?)[\'"],[\s\W\S\w]*},',
        mobile_page
    ).group(1)

    ext = 'mp4'
    type = news_type(url)

    data = {
        "type": type,
        "title": title,
        "source": source,
        "thumbnail_urls": [thumbnail_urls],
        "image_urls": None,
        "video_url": [stream_url],
        "ext": ext,
        "size": None,
    }

    return data


def news_type(url):
    if url:
        return "video"


download = miaopai_download


if __name__ == '__main__':
    data = download("https://weibo.com/tv/v/FxU9HCrbu")
    print(data)