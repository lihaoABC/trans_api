# _*_ coding:utf-8 _*_
import logging
import re
from pyquery import PyQuery as pq
from app.spider_store.utils.content_cleaner import cleaner

from app.spider_store.common import (get_content, get_location)


"""***猎奇网爬虫***"""


def lieqi_news_download(url):
    i = 1
    content_list = []
    title = None
    source = None
    thumbnail_urls = None
    while True:
        if i == 1:
            detail_url = url
        else:
            detail_url = url.replace(".html", '-{}.html'.format(i))
        try:
            html = get_content(detail_url, )
        except Exception:
            raise Exception("获取文章内容超时")
        if re.search(r"很抱歉！您访问页面被外星人劫持了", html):
            break
        doc = pq(html)
        if i == 1:
            # 标题
            title = doc('title').text()
            if not title:
                title = doc("div.contentLtopCnt.clearfix h1.title").text()
            # 来源
            source = doc('div.contentLtopCnt.clearfix div.sourceShare div.source').children()
            # 缩略图
            try:
                thumbnail_urls = re.search(
                    r'var\s*detail_poster_src\s*=\s*[\'|"](.*?)[\'|"]',
                    html
                ).group(1)
                if not re.match(r"http[s]?:", thumbnail_urls):
                    thumbnail_urls = "http:" + thumbnail_urls
                thumbnail_urls = [thumbnail_urls]

            except AttributeError:
                pass
            try:
                source = re.search(r"</span>\s*<span>(.*?)</span>", str(source)).group(1)
            except AttributeError:
                raise AttributeError("获取来源失败")
            # 预处理正文内容
            div = doc('div.contentLtopCnt.clearfix div.contentTextCnt').html()
            content_list.append(str(div))
            i += 1
        else:
            # 预处理正文内容
            div = doc('div.contentLtopCnt.clearfix div.contentTextCnt').html()
            content_list.append(str(div))
            i += 1
        # 阈值
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
            image_url = 'http:' + url
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


def lieqi_video_download(url):
    assert url
    pass


def lieqi_spider(url):
    if news_type(url) == "video":
        return lieqi_video_download(url)
    else:
        return lieqi_news_download(url)


def news_type(url):
    # 判断类型
    # http://www.lieqinews.com/a/n190414105400138.html
    if not url:
        return "video"
    else:
        return "news"


download = lieqi_spider


if __name__ == '__main__':
    url = 'http://www.lieqinews.com/a/n190320202600183.html'
    data = lieqi_spider(url)
    for key, value in data.items():
        print(key+':'+'{}'.format(value))
