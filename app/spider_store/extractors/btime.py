# _*_ coding:utf-8 _*_
import re
import json
from random import random
from urllib.parse import urlparse
from pyquery import PyQuery as pq
from app.spider_store.utils.content_cleaner import cleaner

from app.spider_store.common import (
    match1,
    get_content,
)


"""***北京时间爬虫***"""


def btime_news_download(url):
    html = get_content(url,)
    doc = pq(html)
    # 标题
    title = doc('div.article-container div.article h1#title').text()
    # 来源
    source = doc('div.content-info span.col.cite').text()
    # 预处理正文内容
    content = doc('div.content-text div#content-pure').children()
    content = cleaner(str(content))
    assert content, "获取文章内容失败"
    # 获取文章内图片
    image_urls = re.findall(r'src=[\'|"](.*?)[\'|"]', content, re.S)
    # 获取不到返回空列表
    assert image_urls, "文章中缺少图片"
    image_urls_final = []
    for url in image_urls:
        regex = re.compile(r'http:|https:')
        if regex.match(url):
            image_urls_final.append(url)
        else:
            image_url = 'http:' + url
            image_urls_final.append(image_url)
    # 缩略图
    thumbnail_urls = [image_urls_final[0]]


    data = {
        "type": 'news',
        "title": title,
        "source": source,
        "content": content,
        "thumbnail_urls": thumbnail_urls,
        "image_urls": image_urls_final,
    }

    return data


def btime_video_download(url):
    # html = get_content(url,)
    # title = match1(html, r'var\s*redirect_topic\s*=\s*[\'|"](.*?)[\'|"];')
    # if title is None:
    #     title = match1(html, r'<meta\s*name=[\'|"]description[\'|"]\s*content=[\'|"](.,*?)[\'|"]/>')
    # source = match1(html, r'var\s*d_source\s*=\s*[\'|"](.*?)[\'|"];')
    # if source is None:
    #     source = "crawl"
    # thumbnail_url = match1(html, r'var\s*global_share_img\s*=\s*[\'|"](.*?)[\'|"];')
    # video_url = match1(html, r'var\s*mp4\s*=\s*[\'|"](.*?)[\'|"];')
    # if not re.search(r"http|https", video_url):
    #     video_url = "http:{}".format(video_url)
    # if not re.search(r"http|https", thumbnail_url):
    #     thumbnail_url = "http:{}".format(thumbnail_url)
    #
    #
    # data = {
    #         "type": 'video',
    #         "title": title,
    #         "source": source,
    #         "thumbnail_urls": [thumbnail_url],
    #         "image_urls": None,
    #         "video_url": [video_url],
    #         "ext": None,
    #         "size": None,
    #     }
    #
    # return data
    pass


def btime_spider(url):
    if news_type(url) == "video":
        return btime_video_download(url)
    else:
        return btime_news_download(url)


def news_type(url):
    # 判断类型
    # https://item.btime.com/f7tlsepn2i5942al9u9ale8hdq1
    if not url:
        return "video"
    else:
        return "news"


download = btime_spider


if __name__ == '__main__':
    url = 'https://item.btime.com/066roh277hovin4af62ch84777a'
    data = btime_spider(url)
    print(data)
