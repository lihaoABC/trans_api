from app.spider_store.common import any_download
from app.spider_store.extractors.ifeng import download

# title = any_download(
title = download(
    url='http://v.ifeng.com/201903/video_35324069.shtml',
    # url='http://v.ifeng.com/201902/video_35003754.shtml',
    title="111sasd",
    info_only=False
)

print(title)
