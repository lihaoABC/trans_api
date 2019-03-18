# _*_ coding:UTF-8 _*_
import datetime
import ftplib
import logging
import re
import requests

from app.spider_store.configs import (SITES, POST_API, POST_USER_AGENT, )
from app.spider_store.common import (r1, img_download, download_urls)
from app.spider_store.utils.ftp_client import UploadsFiles
from app.spider_store.run_spider import import_extractor
from app.spider_store.utils.response_code import COD


post_url = POST_API
headers = {
    "User-Agent": POST_USER_AGENT,
    }


def check_url(url, mongo):
    """
    检查url正确性，是否支持一键转换
    :return: site in SITES
    """
    video_host = r1(r'https?://([^/]+)/', url)
    video_url = r1(r'https?://[^/]+(.*)', url)
    if not (video_host and video_url):
        if mongo.exists(url):
            message = r"格式错误"
            mongo.update(url, message)
            raise AssertionError(r"格式错误")
        else:
            message = r"格式错误"
            info = mongo.info(url, message)
            mongo.insert(info)
            raise AssertionError(r"格式错误：{}".format(url))
    assert video_host and video_url, r"格式错误：{}".format(url)
    if video_host.endswith(r'.com.cn') or video_host.endswith(r'.ac.cn'):
        video_host = video_host[:-3]

    logging.debug(r'URL host is {}'.format(video_host))

    domain = r1(r'(\.[^.]+\.[^.]+)$', video_host) or video_host
    k = r1(r'([^.]+)', domain)
    logging.debug("site is {}".format(k))
    if k not in SITES:
        if mongo.exists(url):
            message = r'不支持的url'
            mongo.update(url, message)
            raise AssertionError(r'不支持的url')
        else:
            message = r'不支持的url'
            info = mongo.info(url, message)
            mongo.insert(info)
            raise AssertionError(r'不支持的url')
    else:
        if mongo.exists(url):
            if mongo.block(url):
                message = r'此url重复'
                mongo.update(url, message)
                raise AssertionError(r'此url重复')
        else:
            info = mongo.info(url, COD.BEGIN)
            mongo.insert(info)

    return k


def get_detail_info(k, url, mongo):
    """
    获取视频信息
    :param k: 域
    :return: data>json>title,thumbnailUrls,source,videoUrl
    """

    logging.debug(r'开始获取视频信息')
    mongo.update(url, COD.REDINFO)
    params = import_extractor(k)
    logging.debug("params is {}".format(params))
    data = params.download(url)
    if data is not None:
        logging.debug('Data is %s' % data)
        return data
    else:
        mongo.update(url, COD.NODATA)
        raise AssertionError(u'获取视频信息失败')


def thumbnail_download(data, url, mongo):
    """
    缩略图下载
    :return:      返回信息
    """
    if data['thumbnail_urls'] is not None:
        logging.debug(r'开始下载缩略图: %s' % data['thumbnail_urls'])
        mongo.update(url, COD.REDIMG)
        thumbnail_local_files = img_download(data['thumbnail_urls'])
        if thumbnail_local_files is not None:
            logging.debug(r'下载图片成功')
            mongo.update(url, COD.GETIMG)
            return thumbnail_local_files
        else:
            logging.debug(r'下载图片失败')
            mongo.update(url, COD.IMGERR)
            raise AssertionError(r'下载缩略图失败')
    else:
        # 使用openCV生成缩略图，暂未开发
        logging.debug(r'缩略图为空，使用openCV生成缩略图，暂未开发')
        pass


def video_download(data, url, mongo, **kwargs):
    """
    根据url下载视频
    :return:
    """
    logging.debug(r'开始下载视频: %s' % data['video_url'])
    mongo.update(url, COD.REDVIDEO)
    if data['video_url'] is not None:
        video_local_files = download_urls(
            [data["video_url"]],
            data["ext"],
            data["size"],
            output_dir=data["output_dir"],
            merge=True,
            **kwargs
        )
        if video_local_files is not None:
            logging.debug(r'下载视频成功')
            mongo.update(url, COD.GETVIDEO)
        else:
            logging.debug(r"下载视频失败")
            mongo.update(url, COD.VIDEOERR)
            raise AssertionError(r'下载视频失败')
    else:
        logging.debug(r"视频地址为空")
        mongo.update(url, COD.VIDEOERR)
        raise AssertionError(r'下载视频失败')

    return video_local_files


def files_upload(thumbnail_local_files, video_local_files, url, mongo):
    # 上传缩略图
    logging.debug(r'开始上传缩略图')
    uploads = UploadsFiles(thumbnail_local_files)
    f = uploads.uploads()
    if f:
        logging.debug(r'上传缩略图成功')
        mongo.update(url, COD.GETUPIMG)
    else:
        logging.debug(r'上传缩略图失败')
        mongo.update(url, COD.UPLOADERR)
        raise AssertionError(r'上传缩略图失败')

    # 上传视频
    logging.debug(r'开始上传视频')
    uploads = UploadsFiles([video_local_files])
    f = uploads.uploads()
    if f:
        logging.debug(r'上传视频成功')
        mongo.update(url, COD.GETUPVIDEO)
    else:
        logging.debug(r'上传视频失败')
        mongo.update(url, COD.UPLOADERR)
        raise AssertionError(r'上传视频失败')


def post_data(url, category, k, data, thumbnail_local_files, video_local_files):
    logging.debug('生成用来发布的json文件')
    writer = k     # 发布作者
    content = '<video src="{}" controls="controls" autoplay="autoplay" width="100%">' \
                   '您的浏览器不支持 video 标签。</video>'.format(video_local_files)

    pyload = {
        "title": data['title'],
        "writer": writer,
        "befrom": data['source'],
        "newstext": content,
        "sourceurl": url,
        "keyboard": None,
        "titlepic": thumbnail_local_files,
        "titlepic2": None,
        "titlepic3": None,
        "titlepic4": None,
        "classid": category,
        "enews": "AddNews",
        "username": "crawl",
        "oldchecked": 1,
        "ecmscheck": 0,
        "checked": 0,
        "isgood": 0,
        "firsttitle": 0,
        "dokey": 1,
        "copyimg": 0,
        "getfirsttitlepic": 0,
        "istop": 0,
        "newstempid": 0,
        "groupid": 0,
        "userfen": 0,
        "newspath": 'Ymd',
        "info_diyotherlink": 0,
        "addnews": "提交",
        "videotime": '',
        'videourl': video_local_files,
        "videopic": thumbnail_local_files[0],
    }

    return pyload


def post_api(pyload, url, mongo, thumbnail_local_files, video_local_files):
    """
    调用发布接口，发布视频新闻到网站
    :param pyload: json data
    :return:
    """

    r = requests.post(
        url=post_url,
        data=pyload,
        headers=headers,

    )
    logging.debug('已发送')
    if re.search(r'增加信息成功', r.text):
        logging.debug('增加信息成功')
        mongo.update(url, COD.OK)
        return '{"result": "增加信息成功"}'
    else:
        logging.debug('执行文件删除')
        ftp = ftplib.FTP()
        ftp.connect('47.98.221.90', 21)
        ftp.login('ftpnews', 'video293840')
        paths = datetime.datetime.now().strftime('%Y%m%d')
        serverPath = '/' + paths
        try:
            ftp.cwd(serverPath)
        except ftplib.error_perm:
            logging.debug('WRANING: 切换目录失败')
            return
        for img in thumbnail_local_files:
            try:
                ftp.delete(img.split('/')[-1])
                logging.debug('删除:{}==>成功'.format(img))
            except:
                logging.debug('删除:{}==>失败'.format(img))

        try:
            ftp.delete(video_local_files.split('/')[-1])
            logging.debug('删除:{}==>成功'.format(video_local_files))
        except:
            logging.debug('删除:{}==>失败'.format(video_local_files))

        ftp.quit()
        logging.debug('执行成功\n')
        if re.search(r'标题重复,增加不成功!', r.text):
            logging.debug('标题重复,增加不成功!')
            mongo.update(url, COD.EXISTS)
            raise AssertionError(r'标题重复,增加不成功!')
        if re.search(r'您没有增加信息的权限', r.text):
            logging.debug('您没有增加信息的权限')
            mongo.update(url, COD.LIMIST)
            raise AssertionError(r"您没有增加信息的权限")


