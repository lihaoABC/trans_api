# _*_ coding:utf-8 _*_
from lxml import etree
from app.spider_store.common import (
    match1,
    get_content,
)


def bilibili_download(url):
    response = get_content(url)
    html = etree.HTML(response)
    if html.xpath('//title/text()')[0]:
        title = html.xpath('//title/text()')[0]

    elif html.xpath('//meta[@itemprop="name"]/@content')[0]:
        title = html.xpath('//meta[@itemprop="name"]/@content')[0]
    else:
        title = html.xpath('//meta[@property="og:title"]/@content')[0]

    title = match1(title, r'(.*?)_哔哩哔哩')

    if html.xpath('//meta[@itemprop="thumbnailUrl"]/@content'):
        thumbnail_url = html.xpath('//meta[@itemprop="thumbnailUrl"]/@content')
    elif html.xpath('//meta[@itemprop="image"]/@content'):
        thumbnail_url = html.xpath('//meta[@itemprop="image"]/@content')
    else:
        thumbnail_url = html.xpath('//meta[@property="og:image"]/@content')

    source = html.xpath('//meta[@itemprop="author"]/@content')[0]
    video_url = None
    type = news_type(url)

    data = {
        "type": type,
        "title": title,
        "source": source,
        "thumbnail_urls": thumbnail_url,
        "image_urls": None,
        "video_url": video_url,
        "ext": None,
        "size": None,
    }

    return data


def news_type(url):
    if url:
        return "video"


download = bilibili_download


if __name__ == '__main__':
    data = bilibili_download("https://www.bilibili.com/video/av47723266")
    print(data)