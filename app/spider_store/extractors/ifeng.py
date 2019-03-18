# _*_ coding:UTF-8 _*_
import logging
import random
import datetime
from html import unescape
from app.spider_store.common import (
    get_content,
    url_info,
    download_urls,
    match1,
)
from app.spider_store.configs import OUTPUT_DIR, FAKE_USER_AGENT

headers = {
        'user-agent': random.choice(FAKE_USER_AGENT)
    }
output_dir = OUTPUT_DIR + datetime.datetime.now().strftime('%Y%m%d') + '/'


def ifeng_download_by_id(id, title=None, output_dir=output_dir, merge=True, info_only=False):
    assert match1(id, r'([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})'), id
    url = 'http://vxml.ifengimg.com/video_info_new/{}/{}/{}.xml'.format(id[-2], id[-2:], id)
    xml = get_content(url)
    # 标题
    title_real = match1(xml, r'Name="([^"]+)"')
    title_real = unescape(title_real)
    # 来源
    source = match1(xml, r'ColumnName="([^"]+)"')
    source = unescape(source)
    # 缩略图
    thumbnail_urls = match1(xml, 'SmallPosterUrl="([^"]+)"')
    # 视频下载链接
    video_url = match1(xml, r'VideoPlayUrl="([^"]+)"')
    video_url = video_url.replace('http://wideo.ifeng.com/', 'http://ips.ifeng.com/wideo.ifeng.com/')
    type, ext, size = url_info(video_url)
    # print_info(site_info, title, ext, size)
    data = {
        "title": title_real,
        "source": source,
        "thumbnail_urls": thumbnail_urls,
        "video_url": video_url,
    }
    if not info_only:
        download_urls([video_url], title, ext, size, output_dir, merge=merge, headers=headers)

    return data


def ifeng_download(url, title=None, output_dir=output_dir, merge=True, info_only=False, **kwargs):
    # old pattern /uuid.shtml
    # now it could be #uuid
    id = match1(url, r'([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})')
    if id:
        return ifeng_download_by_id(id, None, output_dir=output_dir, merge=merge, info_only=info_only)

    html = get_content(url)
    uuid_pattern = r'"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})"'
    id = match1(html, r'var vid="([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})"')
    if id is None:
        video_pattern = r'"vid"\s*:\s*' + uuid_pattern
        id = match1(html, video_pattern)
    assert id, "can't find video app"
    return ifeng_download_by_id(id, title=title, output_dir=output_dir, merge=merge, info_only=info_only)


site_info = "ifeng.com"

download = ifeng_download
