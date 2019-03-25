# _*_ codingLUTF-8 _*_
import datetime
import logging
import random
import urllib.parse
from app.spider_store.common import (
    match1,
    url_info,
    get_content,
    download_urls,
    get_output_dir,
)

from app.spider_store.configs import FAKE_USER_AGENT

headers = {
        'user-agent': random.choice(FAKE_USER_AGENT)
    }
output_dir = get_output_dir()


def baomihua_download_by_id(
    _id, title, source, img_url, output_dir=output_dir, merge=True, info_only=False, **kwargs
):
    html = get_content(
        'http://play.baomihua.com/getvideourl.aspx?flvid={}&devicetype='
        'phone_app'.format(_id)
    )
    host = match1(html, r'host=([^&]*)')
    assert host
    _type = match1(html, r'videofiletype=([^&]*)')
    assert _type
    vid = match1(html, r'&stream_name=([^&]*)')
    assert vid
    dir_str = match1(html, r'&dir=([^&]*)').strip()
    video_url = 'http://{}/{}/{}.{}'.format(host, dir_str, vid, _type)
    logging.debug("url is {}".format(url))
    if title is None:
        title = match1(html, r'&title=([^&]*)')
        title = urllib.parse.unquote(title)
    if source is None:
        return None
    if img_url is None:
        img_url = match1(html, r'&video_img=([^&]*)')

    ext = _type
    size = int(match1(html, r'&videofilesize=([^&]*)'))

    data = {
        "title": title,
        "source": source,
        "thumbnail_urls": [img_url],
        "video_url": video_url,
        "ext": ext,
        "size": size,
        "output_dir": output_dir,
    }
    # if not info_only:
    #     video_path = download_urls(
    #         [url], ext, size, output_dir, merge=merge, **kwargs
    #     )

    return data


def baomihua_download(
    url, merge=True, info_only=False, **kwargs
):
    html = get_content(url)
    title = match1(html, r"var\s*temptitle\s*=\s*'(.*?)';")
    assert title
    source = match1(html, r"var\s*appName\s*=\s*\"(.*?)\";")
    assert source
    img_url = match1(html, r"var\s*pic\s*=\s*\"(.*?)\";")
    assert img_url
    _id = match1(html, r'flvid\s*=\s*(\d+)')
    assert _id
    return baomihua_download_by_id(
        _id, title, source, img_url, merge=merge, info_only=info_only,
        **kwargs
    )


download = baomihua_download
