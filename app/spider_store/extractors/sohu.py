# _*_ coding:utf-8 _*_

import re
import json
from pyquery import PyQuery as pq
from app.spider_store.common import (
    match1,
    get_html,
    get_content,
)
from app.spider_store.utils.content_cleaner import cleaner


def sohu_news_download(url,):
    html = get_content(url, )
    doc = pq(html)
    if "www.sohu.com/a/" in url:
        # 标题
        title = doc('div.text div.text-title h1').text()
        if not title:
            title = doc('div.content.area div.article-box.l h3.article-title').text()
        if re.match(r"原创", title):
            title = title.replace("原创", '')
        # 来源
        source = doc('div.column.left div.user-info h4 a').text()
        if not source:
            source = doc('div.right-author-info.clearfix div.l.clearfix a.name.l').text()
        # 预处理正文内容
        content = doc('div.text article.article').html()
        if not content:
            content = doc('article.article-text').html()
        backsohu = re.compile(r"<span\s*class=['|\"]backword['|\"]>.*?</span>")
        editor_name = re.compile(r"<p\s*data-role=['|\"]editor-name['|\"]>.*</p>")
        content = backsohu.sub('', content)
        content = editor_name.sub('', content)
        if re.search(r"（搜狐.*?独家出品 未经许可严禁转载）", content):
            content = re.sub(r'（搜狐.*?独家出品 未经许可严禁转载）', '', content)
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
    elif "sh.focus.cn/zixun/" in url:
        # 标题
        title = doc('div.main-content h1').text()
        if re.match(r"原创", title):
            title = title.replace("原创", '')
        # 来源
        source = doc('div.main-content div.s-pic-info div.info-source span a').text()
        # 预处理正文内容
        content = doc('div.main-content div.info-content').html()
        backsohu = re.compile(r"<span\s*class=['|\"]backword['|\"]>.*?</span>")
        editor_name = re.compile(r"<p\s*data-role=['|\"]editor-name['|\"]>.*</p>")
        content = backsohu.sub('', content)
        content = editor_name.sub('', content)
        if re.search(r"（搜狐.*?独家出品 未经许可严禁转载）", content):
            content = re.sub(r'（搜狐.*?独家出品 未经许可严禁转载）', '', content)
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
    else:
        raise AssertionError("urls检测爬虫异常")

    data = {
        "type": 'news',
        "title": title,
        "source": source,
        "content": content,
        "thumbnail_urls": thumbnail_urls,
        "image_urls": image_urls_final,
    }


    return data


def real_url(fileName, key, ch,):
    url = "https://data.vod.itc.cn/ip?new=" + fileName + "&num=1&key=" + key + "&ch=" + ch + "&pt=1&pg=2&prod=h5n"
    return json.loads(get_html(url))['servers'][0]['url']


def sohu_video_download(url):
    if re.match(r'http[s]?://share\.vrs\.sohu\.com', url):
        vid = match1(url, 'id=(\d+)')
        source = None
    else:
        html = get_content(url, charset="GBK")
        vid = match1(html, r'\Wvid\s*[\:=]\s*[\'"]?(\d+)[\'"]?;')
        if re.search(r"var\s*wm_username='(.*?)';", html):
            source = re.search(r"var\s*wm_username='(.*?)';", html).group(1)
        else:
            source = None
    assert vid, "视频vid获取失败，请检查url"

    if re.match(r'http[s]?://tv\.sohu\.com/', url):
        info = json.loads(get_content(
            'http://hot.vrs.sohu.com/vrs_flash.action?vid={}'.format(vid)
        ))
        if info.get("data") and (info.get("data") is not None):
            for qtyp in ['oriVid', 'superVid', 'highVid', 'norVid', 'relativeId']:
                if 'data' in info:
                    hqvid = info['data'][qtyp]
                else:
                    hqvid = info[qtyp]
                if hqvid != 0 and hqvid != vid:
                    info = json.loads(get_content(
                        'http://hot.vrs.sohu.com/vrs_flash.action?vid={}'.format(
                            hqvid
                        )
                    ))
                    if 'allot' not in info:
                        continue
                    break
            host = info['allot']
            tvid = info['tvid']
            urls = []
            if not source:
                if "wm_data" in info:
                    if 'wm_username' in info["wm_data"]:
                        source = info["wm_data"]["wm_username"]
                    else:
                        source = "crawl"
                else:
                    source = "crawl"
            data = info['data']
            title = data['tvName']
            thumbnail_url = data["coverImg"]
            size = sum(data['clipsBytes'])
            assert len(data['clipsURL']) == len(data['clipsBytes']) == len(data['su'])
            for fileName, key in zip(data['su'], data['ck']):
                urls.append(real_url(fileName, key, data['ch']))

        else:
            info = json.loads(get_content(
                'http://my.tv.sohu.com/play/videonew.do?vid={}&referer='
                'http://my.tv.sohu.com'.format(vid)
            ))
            host = info['allot']
            tvid = info['tvid']
            urls = []
            if not source:
                if "wm_data" in info:
                    if 'wm_username' in info["wm_data"]:
                        source = info["wm_data"]["wm_username"]
                    else:
                        source = "crawl"
                else:
                    source = "crawl"
            data = info['data']
            title = data['tvName']
            thumbnail_url = data["coverImg"]
            size = sum(map(int, data['clipsBytes']))
            assert len(data['clipsURL']) == len(data['clipsBytes']) == len(data['su'])
            for fileName, key in zip(data['su'], data['ck']):
                urls.append(real_url(fileName, key, data['ch']))

        data = {
                "type": 'video',
                "title": title,
                "source": source,
                "thumbnail_urls": [thumbnail_url],
                "image_urls": None,
                "video_url": urls,
                "ext": None,
                "size": size,
            }

        return data
    else:
        return None


def sohu_spider(url):
    if news_type(url) == "video":
        return sohu_video_download(url)
    else:
        return sohu_news_download(url)


def news_type(url):

    if re.match(r"http[s]?://tv\.sohu\.com", url):
        return "video"
    else:
        return "news"


download = sohu_spider


if __name__ == '__main__':
    url = 'https://tv.sohu.com/v/MjAxOTA0MjMvbjYwMDcwMDA0MC5zaHRtbA==.html'     # video
    url2 = 'http://www.sohu.com/a/318287619_428290'     # news
    url3 = 'http://www.sohu.com/a/317886624_383324'     # news
    url4 = 'https://sh.focus.cn/zixun/e24c627c2a5fec58.html'     # news
    # data = sohu_video_download(url)
    data = sohu_spider(url4)
    for key, value in data.items():
        print(key + ':' + '{}'.format(value))
