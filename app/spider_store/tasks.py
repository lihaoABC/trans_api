from app.spider_store.crawler import *
from app.spider_store.utils.redis_queue import RedisQueue
from configs import (Config,)
from celery import Celery
celery = Celery(
        __name__,
        broker=Config.CELERY_BROKER_URL,
        backend=Config.CELERY_RESULT_BACKEND,
    )

celery.autodiscover_tasks(["app.spider_store"])


@celery.task
def main(url, category):
    """
    main program
    :return:
    """
    redis = RedisQueue()
    sha1 = redis.url_sha1(url)
    # k为域
    k = check_url(url, redis, sha1)

    # data为title, thumbnail, source, video_url的json
    data = get_detail_info(k=k, url=url, redis=redis, sha1=sha1)

    # thumbnail_local_files为缩略图服务器地址
    thumbnail_local_files = thumbnail_download(data=data, redis=redis, sha1=sha1)
    # video_local_files为视频的服务器地址
    video_local_files = video_download(k=k, data=data, redis=redis, sha1=sha1)

    state = files_upload(thumbnail_local_files, video_local_files, redis, sha1)
    if state == False:
        raise AssertionError('上传至服务器出现错误')
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
        redis, sha1,
        thumbnail_local_files,
        video_local_files,
    )

    return result
