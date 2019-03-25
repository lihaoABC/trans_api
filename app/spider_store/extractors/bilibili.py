# _*_ coding:utf-8 _*_
import logging

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

    data = {
        "title": title,
        "source": source,
        "thumbnail_urls": thumbnail_url,
        "video_url": video_url,
    }

    return data


download = bilibili_download
