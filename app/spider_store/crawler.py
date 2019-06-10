# _*_ coding:UTF-8 _*_
import re
import ftplib
import logging
import datetime
import hashlib

import requests
from app.spider_store.configs import (
    SITES, POST_HEADERS,
    VIDEO_FTP_HOST, VIDEO_FTP_PORT, VIDEO_FTP_USER, VIDEO_FTP_PASSWORD,
    DOU_POST_API, VIDEO_POST_API)
from app.spider_store.common import (
    match1,
    files_download,
    video_downloads,
    import_extractor,
    generate_thumbnail,

)
from app.spider_store.utils.content_cleaner import content_processing
from app.spider_store.utils.ftp_client import UploadsFiles
from app.spider_store.utils.response_code import COD


def check_url(url, username, mongo):
    """
    检查url正确性，是否支持一键转换
    :return: site in SITES
    """
    video_host = match1(url, r'http[s]?://([^/]+)/')
    logging.debug(video_host)
    video_url = match1(url, r'http[s]?://[^/]+(.*)')
    logging.debug(video_url)
    if re.search(r'\?', video_url):
        if video_host == "www.ku6.com":
            pass
        else:
            url = url.replace(match1(video_url, r'(\?.*)'), '')
    if not (video_host and video_url):
        if mongo.exists(url):
            mongo.update(url, COD.FORMAT)
            raise AssertionError(r"格式错误")
        else:
            info = mongo.info(url, COD.FORMAT, username)
            mongo.insert(info)
            raise AssertionError(r"格式错误：{}".format(url))
    assert video_host and video_url, r"格式错误：{}".format(url)
    if video_host.endswith(r'.com.cn') or video_host.endswith(r'.ac.cn'):
        video_host = video_host[:-3]

    domain = match1(video_host, r'(\.[^.]+\.[^.]+)$') or video_host
    k = match1(domain, r'([^.]+)')
    # acfun临时处理
    if k == "acfun":
        url = url.replace("https", "http")
    # qq临时处理
    if re.search(r"new\.qq\.com", url) or re.search(r"v\.qq\.com", url):
        k = "qq"
    logging.debug("site is {}".format(k))
    if k not in SITES:
        if mongo.exists(url):
            mongo.update(url, COD.URLES)
            raise AssertionError(r'不支持的url, k={}'.format(k))
        else:
            info = mongo.info(url, COD.URLES)
            mongo.insert(info)
            raise AssertionError(r'不支持的url, k={}'.format(k))
    else:
        if mongo.exists(url):
            if mongo.block(url):
                mongo.update(url, COD.URLEX)
                raise AssertionError(r'此url重复')
        else:
            info = mongo.info(url, COD.BEGIN, username)
            mongo.insert(info)

    return k, url


def get_detail_info(k, url, mongo):
    """
    获取视频信息
    :param k: 域
    :return: data>json>title,thumbnailUrls,source,videoUrl
    """

    logging.debug(r'开始获取文章信息')
    mongo.update(url, COD.REDINFO)
    params = import_extractor(k)
    logging.debug("params is {}".format(params))
    try:
        data = params.download(url)
    except Exception as e:
        mongo.update(url, e.args[0])
        raise Exception(e.args)
    try:
        message = data["message"]
        mongo.update(url, message)
        raise Exception(message)
    except KeyError:
        pass
    if data is not None:
        if data["type"] == 'video':
            # logging.debug('Data is %s' % data)
            mongo.update(url, COD.GETVINFO, data["title"])
        else:
            # logging.debug('Data is %s' % data)
            mongo.update(url, COD.GETNINFO, data["title"])
        return data
    else:
        mongo.update(url, COD.NODATA)
        raise AssertionError(u'获取信息失败')


def thumbnail_download(data, k, url, mongo):
    """
    缩略图下载
    :return:      返回信息
    """
    if data['thumbnail_urls'] is not None:
        logging.debug(r'开始下载缩略图: %s' % data['thumbnail_urls'])
        mongo.update(url, COD.REDTHU)
        try:
            referer = url if k != '163' else None     # 网易的图片不加referer
            thumbnail_local_files = files_download(
                data['thumbnail_urls'], referer=referer
            )
        except Exception as e:
            logging.debug(r'下载缩略图失败')
            mongo.update(url, COD.THUERR)
            message = e.args
            raise AssertionError(r'{}:下载缩略图失败,\n message: {}'.format(url, message[0]))
        logging.debug(r'下载缩略图成功')
        mongo.update(url, COD.GETTHU)
        return thumbnail_local_files
    else:
        # 视频使用openCV生成缩略图，暂未开发
        logging.debug(r'缩略图为空，使用openCV生成缩略图，暂未开发')
        mongo.update(url, COD.THUNIL)
        return None


def pic_download(data, k, url, mongo):
    """
    图片下载
    :return:      返回信息
    """
    if data['image_urls'] is not None:
        logging.debug(r'开始下载图片: %s' % data['image_urls'])
        mongo.update(url, COD.REDIMG)
        try:
            referer = url if k != '163' else None  # 网易的图片不加referer
            image_local_files = files_download(
                data['image_urls'], referer=referer
            )
        except Exception as e:
            logging.debug(r'下载图片失败')
            mongo.update(url, COD.IMGERR)
            message = e.args
            raise AssertionError(r'{}:下载文章内图片失败,\n message: {}'.format(url, message[0]))
        logging.debug(r'下载图片成功')
        mongo.update(url, COD.GETIMG)
        return image_local_files
    else:
        mongo.update(url, COD.IMGNIL)
        raise AssertionError(r'{}:图片为空'.format(url))


def video_download(data, url, mongo, **kwargs):
    """
    根据url下载视频
    :return:
    """
    if data['video_url'] is not None:
        logging.debug(r'开始下载视频: {}'.format(url))
        mongo.update(url, COD.REDVIDEO)
        try:
            video_local_files = files_download(
                data["video_url"], referer=url
            )
        except Exception as e:
            logging.debug(r"{}:下载视频失败".format(url))
            mongo.update(url, COD.VIDEOERR)
            message = e.args
            raise AssertionError(r'{}:下载视频失败,\n message: {}'.format(url, message[0]))
        logging.debug(r'{}:下载视频成功'.format(url))
        mongo.update(url, COD.GETVIDEO)
    else:
        video_local_files = video_downloads(kwargs["key"], url, mongo)
        if video_local_files is None:
            mongo.update(url, COD.VIDEOERR)
            raise AssertionError(r'{}:不支持此栏目，下载视频失败'.format(url))
    return video_local_files


def check_thumbnail(video_local_files, url, mongo, **kwargs):
    """
    根据视频生成缩略图
    :param video_local_files:
    :param mongo:
    :param kwargs:
    :return:
    """
    thumbnail_local_files = generate_thumbnail(video_local_files)
    if thumbnail_local_files is not None:
        logging.debug(r'生成缩略图成功')
        mongo.update(url, COD.GETTHU)
        return thumbnail_local_files
    else:
        logging.debug(r'生成缩略图失败')
        mongo.update(url, COD.GENTHUERR)
        raise AssertionError(r'{}:生成缩略图失败'.format(url))


def files_upload(thumbnail_local_files, local_files, url, mongo, data):
    # 上传缩略图
    logging.debug(r'{}:开始上传缩略图'.format(url))
    uploads = UploadsFiles(thumbnail_local_files)
    f = uploads.uploads()
    if f:
        logging.debug(r'{}:上传缩略图成功'.format(url))
        mongo.update(url, COD.GETUPIMG)
    else:
        logging.debug(r'{}:上传缩略图失败'.format(url))
        mongo.update(url, COD.UPLOADERR)
        raise AssertionError(r'{}:上传缩略图失败'.format(url))

    if data["type"] == "video":
        # 上传视频
        logging.debug(r'{}:开始上传视频'.format(url))
        uploads = UploadsFiles(local_files)
        f = uploads.uploads()
        if f:
            logging.debug(r'{}:上传视频成功'.format(url))
            mongo.update(url, COD.GETUPVIDEO)
        else:
            logging.debug(r'{}:上传视频失败'.format(url))
            mongo.update(url, COD.UPLOADERR)
            raise AssertionError(r'{}:上传视频失败'.format(url))
    else:
        # 上传图片
        logging.debug(r'{}:开始上传图片'.format(url))
        uploads = UploadsFiles(local_files)
        f = uploads.uploads()
        if f:
            logging.debug(r'{}:上传图片成功'.format(url))
            mongo.update(url, COD.GETUPIMG)
        else:
            logging.debug(r'{}:上传图片失败'.format(url))
            mongo.update(url, COD.UPLOADERR)
            raise AssertionError(r'{}:上传图片失败'.format(url))


def post_data(url, category, k, data, thumbnail_local_files, local_files, username, mongo):
    if username is None:
        username = 'crawl'
    logging.debug('{}:生成用来发布的json文本'.format(url))
    writer = k     # 发布作者
    if data["type"] == "video":
        content = '<video src="{}" controls="controls" autoplay="autoplay" width="100%">' \
                  '您的浏览器不支持 video 标签。</video>'.format(local_files[0])

        pyload = {
            "title": data['title'],
            "writer": writer,
            "befrom": data['source'],
            "newstext": content,
            "sourceurl": url,
            "keyboard": None,
            "titlepic": thumbnail_local_files[0],
            "titlepic2": None,
            "titlepic3": None,
            "titlepic4": None,
            "classid": category,
            "enews": "AddNews",
            "username": username,
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
            'videourl': local_files[0],
            "videopic": thumbnail_local_files[0],
        }



    else:
        # 正文处理
        try:
            content = content_processing(data['content'], local_files)
        except Exception as e:
            mongo.update(url, e.args[0])
            raise Exception("图片下载不全，发布失败")

        # 生成简介
        try:
            regex = re.compile(r"<p>([^<]+)</p>")
            introduction = regex.search(content).group(1)
        except Exception:
            introduction = None

        # 生成key
        # php: md5('f4b45932ac18374b2c8c131eb501d238'.$username)
        key = hashlib.md5("f4b45932ac18374b2c8c131eb501d238{}".format(username).encode()).hexdigest()

        pyload = {
            "enews": "AddNews",
            "username": username,
            "key": key,
            "classid": category,
            "title": data['title'],
            "labels": None,
            "smalltext": introduction,
            "writer": writer,
            "befrom": data['source'],
            "sourceurl": url,
            "newstext": content,
            "titlepic": thumbnail_local_files[0],
            "titlepic2": None,
            "titlepic3": None,
            "titlepic4": None,
            'videourl': None,
            "musicurl": None,
            "musiccomposer": None,
            "musicwriter": None,
        }

    return pyload


def post_api(cate, pyload, url, mongo, thumbnail_local_files, local_files):
    """
    调用发布接口，发布视频新闻到网站
    :param pyload: json data
    :return:
    """
    if cate == "news":
        post_api = DOU_POST_API
    else:
        post_api = VIDEO_POST_API

    r = requests.post(
        url=post_api,
        data=pyload,
        headers=POST_HEADERS,

    )
    logging.debug('{}:已发送'.format(url))
    if re.search(r'增加信息成功', r.text):
        logging.debug('{}:增加信息成功'.format(url))
        mongo.update(url, COD.OK)
        mongo.complite(url)
        return '{"log": "%s：增加信息成功"}' % url
    else:
        if cate == "news":
            if re.search(r'标题重复,增加不成功!', r.text):
                logging.debug('{}:标题重复,增加不成功!'.format(url))
                mongo.update(url, COD.EXISTS)
                raise AssertionError(r'标题重复,增加不成功!')
            elif re.search(r'您没有增加信息的权限', r.text):
                logging.debug('{}:您没有增加信息的权限'.format(url))
                mongo.update(url, COD.LIMIST)
                raise AssertionError(r"您没有增加信息的权限")
            elif re.search(r"<html.*>", r.text):
                logging.debug("未知错误，发布失败")
                text = re.search(
                    r"<div\s*align=['|\"]center['|\"]>\s*<br>\s*<b>(.*?)</b>\s*<br>",
                    r.text
                ).group(1)
                mongo.update(url, "未知错误:{}".format(text))
                raise AssertionError("未知错误:{}".format(text))
            else:
                logging.debug(r.text)
                mongo.update(url, r.text)
                raise AssertionError(r.text)
        else:
            logging.debug('{}:执行文件删除'.format(url))
            ftp = ftplib.FTP()
            ftp.connect(VIDEO_FTP_HOST, VIDEO_FTP_PORT)
            ftp.login(VIDEO_FTP_USER, VIDEO_FTP_PASSWORD)
            paths = datetime.datetime.now().strftime('%Y%m%d')
            serverPath = '/' + paths
            try:
                ftp.cwd(serverPath)
            except ftplib.error_perm:
                logging.debug('{}:WRANING: 切换目录失败'.format(url))
                return
            for img in thumbnail_local_files:
                try:
                    ftp.delete(img.split('/')[-1])
                    logging.debug('删除:{}==>成功'.format(img))
                except Exception:
                    logging.debug('删除:{}==>失败'.format(img))

            for file in local_files:

                try:
                    ftp.delete(file.split('/')[-1])
                    logging.debug('删除:{}==>成功'.format(file))
                except Exception:
                    logging.debug('删除:{}==>失败'.format(file))

            ftp.quit()
            logging.debug('执行成功\n')

            if re.search(r'标题重复,增加不成功!', r.text):
                logging.debug('{}:标题重复,增加不成功!'.format(url))
                mongo.update(url, COD.EXISTS)
                raise AssertionError(r'标题重复,增加不成功!')
            if re.search(r'您没有增加信息的权限', r.text):
                logging.debug('{}:您没有增加信息的权限'.format(url))
                mongo.update(url, COD.LIMIST)
                raise AssertionError(r"您没有增加信息的权限")



