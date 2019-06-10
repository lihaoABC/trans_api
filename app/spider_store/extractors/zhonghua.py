# _*_ coding:utf-8 _*_
import logging
import re
from pyquery import PyQuery as pq
from app.spider_store.utils.content_cleaner import cleaner

from app.spider_store.common import (get_content,)


"""***中华网爬虫***"""


def zhonghua_news_download(url):
    i = 1
    content_list = []
    title = None
    source = None
    thumbnail_urls = None
    while True:
        if i == 1:
            detail_url = url
        else:
            detail_url = url.replace(".html", '_{}.html'.format(i))
        try:
            html = get_content(detail_url, )
        except Exception:
            raise Exception("获取文章内容超时")
        doc = pq(html)
        if i == 1:
            # 标题
            title = doc("div.pleft.mt10 div.article-header h1.title").text()
            # 来源
            source = doc('div.pleft.mt10 div.article-header div.info div.left small#article-source').text()
            # 预处理正文内容
            div = doc('div.pleft.mt10 div.viewbox div#main-content').html()
            content_list.append(str(div))
            i += 1
        else:
            # 预处理正文内容
            div = doc('div.pleft.mt10 div.viewbox div#main-content').html()
            content_list.append(str(div))
            i += 1
        if not re.search(r"下一页</a>", html):
            break
        if i >= 30:
            break

    try:
        content = ''.join(content_list)
        content = cleaner(content)
        logging.debug('清洗完成')
    except:
        raise AssertionError("获取文章内容失败")

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
            image_url = 'http://kan.china.com' + url
            image_urls_final.append(image_url)
    # 缩略图
    if not thumbnail_urls:
        thumbnail_urls = [image_urls_final[0]]

    if (title and source):
        data = {
            "type": 'news',
            "title": title,
            "source": source,
            "content": content,
            "thumbnail_urls": thumbnail_urls,
            "image_urls": image_urls_final,
        }
    else:
        raise Exception("获取标题和来源失败")

    return data


def zhonghua_video_download(url):
    assert url
    pass


def zhonghua_spider(url):
    if news_type(url) == "video":
        return zhonghua_video_download(url)
    else:
        return zhonghua_news_download(url)


def news_type(url):
    # 判断类型
    # https://kan.china.com/article/582319.html
    if not url:
        return "video"
    else:
        return "news"


download = zhonghua_spider


if __name__ == '__main__':
    url = 'https://kan.china.com/article/582319.html'
    data = zhonghua_spider(url)
    for key, value in data.items():
        print(key+':'+'{}'.format(value))
