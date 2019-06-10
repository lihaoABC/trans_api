# _*_ coding:utf-8 _*_
import re
from pyquery import PyQuery as pq
from app.spider_store.utils.content_cleaner import cleaner

from app.spider_store.common import (get_content,)


"""***网易新闻爬虫***"""


def wangyi_news_download(url):
    html = get_content(url, charset="GBK")
    doc = pq(html)
    # 标题
    title = doc('div.post_content_main h1').text()
    assert title, "获取文章标题失败"
    # 来源
    source = doc('div.post_content_main div.post_time_source a#ne_article_source').text()
    assert source, "获取文章来源失败"
    # 预处理正文内容
    # content = doc('div.post_content_main div.post_body').html()
    content = doc('div.post_content_main div.post_body div.post_text').html()
    back = re.compile(r"<div\s*class=['|\"]ep-source\s*cDGray['|\"]>[\s\S\w\W]*?</div>")
    content = back.sub('', content, re.S)
    content = cleaner(str(content))
    assert content, "获取文章内容失败"
    # 获取文章内图片
    image_urls = re.findall(r'src=[\'|"](.*?)[\'|"]', content, re.S)
    if not image_urls:
        image_urls = re.findall(r'data-original=[\'|"](.*?)[\'|"]', content, re.S)
    # 获取不到返回空列表
    assert image_urls, "获取文章图片失败"
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


def wangyi_video_download(url):
    assert url
    pass


def wangyi_spider(url):
    if news_type(url) == "video":
        return wangyi_video_download(url)
    else:
        return wangyi_news_download(url)


def news_type(url):
    # 判断类型
    # https://news.163.com/19/0603/17/EGP0HUVJ0001899N.html
    if not url:
        return "video"
    else:
        return "news"


download = wangyi_spider


if __name__ == '__main__':
    url = 'https://news.163.com/19/0603/17/EGP0HUVJ0001899N.html'
    url2 = 'https://news.163.com/19/0603/13/EGOI28180001875O.html'
    url3 = 'http://home.163.com/19/0514/07/EF4BCD5A001081EI.html'
    url4 = 'https://money.163.com/19/0603/14/EGOL099E002580S6.html'

    data = wangyi_spider(url4)
    for key, value in data.items():
        print(key+':'+'{}'.format(value))
