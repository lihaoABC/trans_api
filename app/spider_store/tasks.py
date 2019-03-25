from app.spider_store.crawler import *
from app.spider_store.utils.mongo_queue import MongoWare
from configs import (Config,)
from celery import Celery
celery = Celery(
        __name__,
        broker=Config.CELERY_BROKER_URL,
        backend=Config.CELERY_RESULT_BACKEND,
    )

celery.autodiscover_tasks(["app.spider_store"])


# @celery.task
def main(url, category):
    """
    main program
    :return:
    """
    mongo = MongoWare()
    # k为域
    k = check_url(url, mongo)

    # data为title, thumbnail, source, video_url的json
    data = get_detail_info(k=k, url=url, mongo=mongo)

    # thumbnail_local_files为缩略图服务器地址
    thumbnail_local_files = thumbnail_download(data, url, mongo)
    # video_local_files为视频的服务器地址
    video_local_files = video_download(data, url, mongo, key=k)

    files_upload(thumbnail_local_files, video_local_files, url, mongo)

    json_data = post_data(
        url,
        category,
        k,
        data,
        thumbnail_local_files,
        video_local_files,
    )
    result = post_api(
        json_data,
        url,
        mongo,
        thumbnail_local_files,
        video_local_files,
    )

    return result

