# _*_ coding:utf-8 _*_

import re
import json
import logging
from pyquery import PyQuery as pq
from app.spider_store.common import (
    match1,
    get_html,
    get_content,
)
from app.spider_store.utils.content_cleaner import cleaner


def eastday_news_download(url):
    i = 1
    content_list = []
    title = None
    source = None
    while True:
        if i == 1:
            detail_url = url
        else:
            detail_url = url.replace(".html", '-{}.html'.format(i))
        try:
            html = get_content(detail_url,)
        except Exception:
            raise Exception("获取文章内容超时")
        if re.search(r'<div class="detail_room">', html):
            logging.debug('东方号内容,发布失败')
            raise Exception('东方号内容,发布失败')
        if re.search(r"404&nbsp;&nbsp;很抱歉！您访问页面被外星人劫持了", html):
            break
        doc = pq(html)
        if i == 1:
            # 标题
            title = doc('div.detail_left_cnt div.J-title_detail.title_detail h1 span').text()
            # 来源
            source = doc(
                'div.detail_left_cnt div.J-title_detail.title_detail div.share_cnt_p.clearfix div.fl'
            ).children()
            try:
                source = re.search(r"</i>\s*<i>(.*?)</i>", str(source)).group(1)
            except AttributeError:
                source = re.search(r"</i>\s*<a.*>(.*?)</a>", str(source), re.S).group(1)
            # 预处理正文内容
            div = doc('div#J-contain_detail_cnt').html()
            content_list.append(str(div))
            i += 1
        else:
            # 预处理正文内容
            div = doc('div#J-contain_detail_cnt').html()
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


def real_url(fileName, key, ch,):
    url = "https://data.vod.itc.cn/ip?new=" + fileName + "&num=1&key=" + key + "&ch=" + ch + "&pt=1&pg=2&prod=h5n"
    return json.loads(get_html(url))['servers'][0]['url']


def eastday_video_download(url):
    html = get_content(url,)
    title = match1(html, r'var\s*redirect_topic\s*=\s*[\'|"](.*?)[\'|"];')
    if title is None:
        title = match1(html, r'<meta\s*name=[\'|"]description[\'|"]\s*content=[\'|"](.,*?)[\'|"]/>')
    source = match1(html, r'var\s*d_source\s*=\s*[\'|"](.*?)[\'|"];')
    if source is None:
        source = "crawl"
    thumbnail_url = match1(html, r'var\s*global_share_img\s*=\s*[\'|"](.*?)[\'|"];')
    video_url = match1(html, r'var\s*mp4\s*=\s*[\'|"](.*?)[\'|"];')
    if not re.search(r"http|https", video_url):
        video_url = "http:{}".format(video_url)
    if not re.search(r"http|https", thumbnail_url):
        thumbnail_url = "http:{}".format(thumbnail_url)


    data = {
            "type": 'video',
            "title": title,
            "source": source,
            "thumbnail_urls": [thumbnail_url],
            "image_urls": None,
            "video_url": [video_url],
            "ext": None,
            "size": None,
        }

    return data


def eastday_spider(url):
    if news_type(url) == "video":
        return eastday_video_download(url)
    else:
        return eastday_news_download(url)


def news_type(url):

    if re.match(r"^http[s]?://video\.eastday\.com/a/\d+\.html$", url):
        return "video"
    else:
        return "news"


download = eastday_spider


if __name__ == '__main__':
    url = 'https://video.eastday.com/a/190424174417088400951.html'
    url2 = "http://mini.eastday.com/a/190531150700421.html"
    data = eastday_spider(url2)
    for key, value in data.items():
        print(key + ':' + '{}'.format(value))
