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


"""***快资讯爬虫***"""


def kuaizixun_news_download(url):
    html = get_content(url,)
    doc = pq(html)
    # 标题
    title = doc('section#main article#bd_article h1#bd_article_title').text()
    # 来源
    source = doc('section#main article#bd_article p.article-info a.source').text()
    # 预处理正文内容
    content = doc('section#main article#bd_article article.content').html()
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


def kuaizixun_video_download(url):
    assert url
    pass


def kuaizixun_spider(url):
    if news_type(url) == "video":
        return kuaizixun_video_download(url)
    else:
        return kuaizixun_news_download(url)


def news_type(url):
    # 判断类型
    # https://sh.qihoo.com/9a9004d8028f07d1a
    if not url:
        return "video"
    else:
        return "news"


download = kuaizixun_spider


if __name__ == '__main__':
    url = 'https://sh.qihoo.com/9a9004d8028f07d1a'
    data = download(url)
    for key, value in data.items():
        print(key+':'+'{}'.format(value))
