import datetime
import os
import random
import logging
import re
import time
import requests
from requests.adapters import HTTPAdapter
from app.spider_store.configs import SITES, FAKE_USER_AGENT
from app.spider_store.run_spider import import_extractor
from app.spider_store.configs import OUTPUT_DIR


class VideoDownload(object):

    def __init__(self, url):
        self.url = url
        self.videoPath = OUTPUT_DIR
        self.video_name = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f') + 'a'
        self.video_path = datetime.datetime.now().strftime('%Y%m%d')
        self.file_path = self.videoPath + self.video_path + '/'
        self.filename = os.path.join(self.file_path + self.video_name + '.mp4')
        self.headers = {
            'user-agent': random.choice(FAKE_USER_AGENT),
        }


    def video_url_download(self):

        s = requests.Session()
        s.mount('http://', HTTPAdapter(max_retries=3))
        s.mount('https://', HTTPAdapter(max_retries=3))

        if self.url is None:
            logging.debug('视频地址为空')
            return None

        if not os.path.isdir(self.videoPath):
            os.mkdir(self.videoPath)

        logging.debug("下载sss: %s" % self.url)
        # 未能正确获得网页 就进行异常处理
        # res = None
        try:
            res = s.get(
                url=self.url,
                headers=self.headers,
                timeout=(5, 15)
            )
            time.sleep(random.random()*4)
            if res.status_code != 200:
                logging.debug('未下载成功：%s' % self.url)
                return None
        except Exception as e:
            logging.debug('未下载成功：%s' % self.url)
            return None

        if not os.path.isdir(self.file_path):
            os.makedirs(self.file_path)
        try:
            if res.content == b'' or None or '':
                logging.debug('内容为空，不执行保存')
                return None
            else:
                with open(self.filename, 'wb') as f:
                    f.write(res.content)
                    logging.debug('下载完成\n')
                local_video_url = 'http://img.dou.gxnews.com.cn/' + self.video_path + '/' + self.video_name + '.mp4'  # 传入上传成功的路径
                return local_video_url
        except:
            logging.debug('下载失败\n')
            return None

    def detail_url_download(self, k):
        params = import_extractor(k, sites=SITES)
        try:
            params.download(self.url, title=self.video_name, info_only=False)
            local_video_url = 'http://img.dou.gxnews.com.cn/' + self.video_path + '/' + self.video_name + '.mp4'  # 传入上传成功的路径
            return local_video_url
        except:
            return None

