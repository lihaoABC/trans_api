from app.spider_store.crawler import *
from app.spider_store.utils.mongo_queue import MongoWare
from configs import (Config,)
from celery import Celery
celery = Celery(
        __name__,
        broker=Config.CELERY_BROKER_URL,
        backend=Config.CELERY_RESULT_BACKEND,
    )


# @celery.task
def main(url, category, username=None,):
    """
    main program
    :return:
    """
    mongo = MongoWare()
    # k为域
    k, _url = check_url(url, username, mongo)

    # data为title, thumbnail, source, video_url的json
    data = get_detail_info(k=k, url=_url, mongo=mongo)

    # thumbnail_local_files为缩略图服务器地址
    thumbnail_local_files = thumbnail_download(data, k, _url, mongo)
    if data["type"] == "video":
        # video_local_files为视频的服务器地址
        local_files = video_download(data, _url, mongo, key=k)
    else:
        local_files = pic_download(data, k, _url, mongo)
    if thumbnail_local_files is None:
        thumbnail_local_files = check_thumbnail(local_files, _url, mongo)

    files_upload(thumbnail_local_files, local_files, _url, mongo, data)

    if data["type"] == "video":
        json_data = post_data(
            _url,
            category,
            k,
            data,
            thumbnail_local_files,
            local_files,
            username,
            mongo,
        )
    else:
        # 增加图文站后修改
        json_data = post_data(
            _url,
            category,
            k,
            data,
            thumbnail_local_files,
            local_files,
            username,
            mongo,
        )
    result = post_api(
        data["type"],
        json_data,
        _url,
        mongo,
        thumbnail_local_files,
        local_files,
    )

    return result

