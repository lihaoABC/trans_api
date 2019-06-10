# _*_ coding:utf-8 _*_
import re
from pyquery import PyQuery as pq
from app.spider_store.utils.content_cleaner import cleaner

from app.spider_store.common import (get_content,)


"""***zaker爬虫***"""


def zaker_news_download(url):
    html = get_content(url,)
    doc = pq(html)
    # 标题
    title = doc('div#article div.article_header h1').text()
    assert title, "获取文章标题失败"
    # 来源
    source = doc('div#article div.article_header div.article_tips a span.auther').text()
    assert source, "获取文章来源失败"
    # 预处理正文内容
    content = doc('div#article div.article_content div#content').html()
    content = cleaner(str(content))
    assert content, "获取文章内容失败"
    # 获取文章内图片
    image_urls = re.findall(r'src=[\'|"](.*?)[\'|"]', content, re.S)
    if not image_urls:
        image_urls = re.findall(r'data-original=[\'|"](.*?)[\'|"]', content, re.S)
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


def zaker_video_download(url):
    assert url
    pass


def zaker_spider(url):
    if news_type(url) == "video":
        return zaker_video_download(url)
    else:
        return zaker_news_download(url)


def news_type(url):
    # 判断类型
    # http://www.myzaker.com/article/5cf0780032ce402e1200000c/
    if not url:
        return "video"
    else:
        return "news"


download = zaker_spider


if __name__ == '__main__':
    url = 'http://www.myzaker.com/article/5cf0b07432ce402212000023/'
    data = zaker_spider(url)
    for key, value in data.items():
        print(key+':'+'{}'.format(value))
