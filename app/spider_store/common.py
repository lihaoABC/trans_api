# _*_ coding:UTF-8 _*_

import datetime
import io
import os
import random
import re
import subprocess
import sys
import time
import locale
import logging
from PIL import Image
from urllib import request, parse
import urllib3

import requests
from requests.adapters import HTTPAdapter

from importlib import import_module
from app.spider_store.configs import SITES

from app.spider_store.configs import (FAKE_HEADERS, OUTPUT_DIR, DOU_POST_HOST, POST_USER_AGENT)
from app.spider_store.utils.response_code import COD

# 改变默认编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')


dry_run = False
json_output = False
force = False
extractor_proxy = None
cookies = None
output_filename = None
auto_rename = False
fake_headers = FAKE_HEADERS

if sys.stdout.isatty():
    default_encoding = sys.stdout.encoding.lower()
else:
    default_encoding = locale.getpreferredencoding().lower()


# disable SSL verify=False warning
urllib3.disable_warnings()
session = requests.Session()
session.mount('http://', HTTPAdapter(max_retries=3))
session.mount('https://', HTTPAdapter(max_retries=3))


def import_extractor(k, sites=SITES):
    if k in sites:
        params = import_module('app.spider_store.extractors.'+sites[k])
        return params
    else:
        return "模块不存在"


def get_output_dir():
    return OUTPUT_DIR + datetime.datetime.now().strftime('%Y%m%d') + '/'


def get_output_name():
    return datetime.datetime.now().strftime('%Y%m%d%H%M%S%f') + 'a'


def get_second_dir():
    return datetime.datetime.now().strftime('%Y%m%d')


def change_jpg(before_path, after_path):
    im = Image.open(before_path)
    im.save(after_path)


def files_download(urls, referer=None, cookies=None, fileinfo=None):
    """
    文件下载
    :param urls: 文件连接[列表]
    :return: 上传后的地址列表
    """
    assert urls, "文件地址为空"
    uploads_paths = []
    local_paths = []

    for url in urls:
        if re.search(r"http[s]?://None", url):
            raise AssertionError("url格式获取不正确，{}".format(url))
        logging.debug('开始下载: {}'.format(url))
        file_name = get_output_name()
        file_path = get_output_dir()
        if not os.path.isdir(file_path):
            try:
                os.mkdir(file_path)
            except:
                os.makedirs(file_path)
        if referer:
            headers = {
                'referer': referer,
                'user-agent': POST_USER_AGENT
            }
        else:
            headers = {
                'user-agent': POST_USER_AGENT
            }

        header = get_head(url, headers=headers, cookies=cookies)
        ext = header["Content-Type"].split('/')[-1]
        type = header["Content-Type"].split('/')[0]
        try:
            length = header["Content-Length"]
        except Exception:
            length = None
        if fileinfo:
            size = fileinfo["size"]
            if size is None:
                size = length
        else:
            size = length
        if size is not None:
            size = float("{:.2f}".format(int(size) / 1024 / 1024))
            if size >= float(100):
                raise AssertionError("文件过大:{}MB".format(size))
        response = urlopen_with_retry(url, headers=headers, timeout=(5, 15))
        time.sleep(random.random())
        if response.status_code != 200:
            raise Exception('未下载成功:{}'.format(url))
        data = response.content
        filename = os.path.join('{}{}.{}'.format(file_path, file_name, ext))

        if not os.path.isdir(os.path.dirname(filename)):
            try:
                os.makedirs(os.path.dirname(filename))
            except Exception as e:
                logging.debug(e.args)
                os.mkdir(os.path.dirname(filename))
        try:
            if data == b'' or None or '':
                logging.debug('内容为空，不执行保存')
                raise AssertionError('内容为空，不执行保存')
            else:
                with open(filename, 'wb') as f:
                    f.write(data)
                    logging.debug('下载完成\n')
                local_paths.append(filename)

        except Exception as e:
            logging.debug(e.args)
            logging.debug('下载失败\n')
            raise AssertionError("下载失败")
        time.sleep(random.random())
        if (type == "video") and (len(urls) > 1):
            return ffmpeg_concat_mp4_to_mp4(local_paths)
        path = get_second_dir() + '/'
        # webp格式转换jpg
        if ext == "webp":
            new_ext = "jpeg"
            new_filename = os.path.join('{0}{1}.{2}'.format(file_path, file_name, new_ext))
            os.rename(filename, new_filename)
            # 先更改filename，后用方法change_jpg
            change_jpg(new_filename, new_filename)
            uploads_paths.append('{0}{1}{2}.{3}'.format(DOU_POST_HOST, path, file_name, new_ext))  # 传入上传成功的路径
        else:
            uploads_paths.append('{0}{1}{2}.{3}'.format(DOU_POST_HOST, path, file_name, ext))  # 传入上传成功的路径
    logging.debug("uploads:{}".format(uploads_paths))
    return uploads_paths


def video_downloads(key, url, mongo):
    uploads_path = []
    filename = get_output_name()
    path = get_output_dir()
    second_path = get_second_dir() + '/'
    a = subprocess.run(['you-get', '-i', url], stdout=subprocess.PIPE)
    dash = a.stdout.decode().replace(' ', '').replace('\n', '')
    logging.debug("dash is {}".format(dash))
    if not dash:
        return None
    _format = re.findall(r"format:(.*?)container:(.*?)quality", dash, re.S)
    if _format != []:
        _format = dict(_format)
        for d in list(_format.keys()):
            rd = repr(d).replace(r"\x1b[0m'", '').replace(r"'\x1b[7m", '')
            _format[rd] = _format.pop(d)
        logging.debug("dash_dict is {}".format(_format))
        if key == "bilibili":
            if 'dash-flv360' in list(_format.keys()):
                ext = _format["dash-flv360"]
                if ext == "mp4":
                    try:
                        subprocess.check_call(
                            ['you-get',
                             '--format=dash-flv360',
                             '-o',
                             '{}'.format(path),
                             '-O',
                             '{}'.format(filename),
                             url],
                            shell=False
                        )
                        logging.debug(r'{}:下载视频成功'.format(url))
                        mongo.update(url, COD.GETVIDEO)
                        uploads_path.append("{}{}{}.{}".format(DOU_POST_HOST, second_path, filename, ext))
                        return uploads_path
                    except Exception:
                        logging.debug(r"{}:执行视频下载失败".format(url))
                        mongo.update(url, COD.VIDEOERR)
                        raise Exception("{}:执行视频下载失败".format(url))

            else:
                try:
                    subprocess.check_call(
                        ['you-get',
                         '--format=flv360',
                         '-o',
                         '{}'.format(path),
                         '-O',
                         '{}'.format(filename),
                         url],
                        shell=False
                    )
                    logging.debug(r'{}:下载视频成功'.format(url))
                    mongo.update(url, COD.GETVIDEO)
                    logging.debug(r"{}:视频转码中".format(url))
                    mongo.update(url, COD.RESET)
                    subprocess.check_call(
                        ['ffmpeg',
                         '-i',
                         '{}'.format(path + filename + '.flv'),
                         '{}'.format(path + filename + '.mp4'),
                         ],
                        shell=False
                    )
                    logging.debug(r"{}:视频转码成功".format(url))
                    mongo.update(url, COD.RESOK)
                    uploads_path.append("{}{}{}.{}".format(DOU_POST_HOST, second_path, filename, "mp4"))
                    return uploads_path
                except Exception:
                    logging.debug(r"{}:执行视频下载失败".format(url))
                    mongo.update(url, COD.VIDEOERR)
                    raise Exception("{}:执行视频下载失败".format(url))
        else:
            try:
                subprocess.check_call(
                    ['you-get',
                     '--itag=18',
                     '-o',
                     '{}'.format(path),
                     '-O',
                     '{}'.format(filename),
                     url],
                    shell=False
                )
                logging.debug(r'{}:下载视频成功'.format(url))
                mongo.update(url, COD.GETVIDEO)

                uploads_path.append("{}{}{}.{}".format(DOU_POST_HOST, second_path, filename, "mp4"))
                return uploads_path
            except Exception:
                logging.debug(r"{}:执行视频下载失败".format(url))
                mongo.update(url, COD.VIDEOERR)
                raise Exception("{}:执行视频下载失败".format(url))

    else:
        try:
            subprocess.check_call(
                ['you-get',
                 '-o',
                 '{}'.format(path),
                 '-O',
                 '{}'.format(filename),
                 url],
                shell=False
            )
            logging.debug(r'{}:下载视频成功'.format(url))
            mongo.update(url, COD.GETVIDEO)
            try:
                size = re.search(r"Size:(.*?)MiB", dash, re.S).group(1)
                logging.debug("Size is {}".format(size))
            except Exception:
                size = None
            if size is not None:
                if float(size) >= float(50):
                    new_filename = get_output_name()
                    logging.debug(r"{}:视频转码中".format(url))
                    mongo.update(url, COD.RESET)
                    subprocess.check_call(
                        ['ffmpeg',
                         '-i',
                         '{}'.format(path + filename + '.mp4'),
                         '-b:v',
                         '512k',
                         '{}'.format(path + new_filename + '.mp4'),
                         '-y'
                         ],
                        shell=False
                    )
                    uploads_path.append("{}{}{}.{}".format(DOU_POST_HOST, second_path, filename, "mp4"))
                    return uploads_path

            uploads_path.append("{}{}{}.{}".format(DOU_POST_HOST, second_path, filename, "mp4"))
            return uploads_path

        except Exception:
            logging.debug(r"{}:执行视频下载失败".format(url))
            mongo.update(url, COD.VIDEOERR)
            raise Exception("{}:执行视频下载失败".format(url))


def generate_thumbnail(video_local_files,):
    """
    根据视频生成缩略图
    :param video_local_files:
    :return:
    """
    thumbnail = []
    logging.debug("生成缩略图中")
    filename = video_local_files.split('/')[-1]
    path = get_output_dir() + filename
    second_path = get_second_dir() + '/'
    thumbnail_path = re.sub(r'(\..*$)', '.jpg', path)
    thumbnail_name = re.sub(r'(\..*$)', '.jpg', filename)

    # time ffmpeg -ss 00:00:06 -i /Users/lihao/Desktop/1/x.mp4 -f image2 -y /Users/lihao/Desktop/1/test2.jpg
    try:
        subprocess.check_call(
            [
                "time",
                'ffmpeg',
                'ss',
                '00:00:06',
                '-i',
                '{}'.format(path),
                '-f',
                'image2',
                '-y',
                '{}'.format(thumbnail_path),
             ],
            shell=False
        )
        time.sleep(random.random())
        thumbnail.append('{}{}.{}'.format(DOU_POST_HOST, second_path, thumbnail_name))  # 传入上传成功的路径
        thumbnail.append(thumbnail_path)
        return thumbnail

    except Exception as e:
        logging.debug('生成缩略图失败：{}'.format(e.args))
        return None


def ffmpeg_concat_mp4_to_mp4(local_paths):
    uploads_path = []
    ts_path = []
    logging.debug('开始合并视频')
    for i, url in enumerate(local_paths):
        mp4_name = url.split('/')[-1]
        ts_name = mp4_name.replace('mp4', 'ts')
        new_file = url.replace(mp4_name, ts_name)
        try:
            subprocess.check_call(
                ['ffmpeg',
                 '-i',
                 '{}'.format(url),
                 '-vcodec',
                 'copy',
                 '-acodec',
                 'copy',
                 '-vbsf',
                 'h264_mp4toannexb',
                 '{}'.format(new_file),
                 ],
                shell=False
            )
            ts_path.append(new_file)
        except:
            raise AssertionError("转换mp4为ts文件失败")

    # 'ffmpeg -i "concat:1.ts|2.ts" -acodec copy -vcodec copy -absf aac_adtstoasc output.mp4'
    filename = get_output_name()
    path = get_output_dir()
    second_path = get_second_dir() + '/'
    concat = "concat:{}".format('|'.join(ts_path))
    filename_path = "{}{}.mp4".format(path, filename)

    try:
        subprocess.check_call(
            ['ffmpeg',
             '-i',
             '{}'.format(concat),
             '-acodec',
             'copy',
             '-vcodec',
             'copy',
             '-absf',
             'aac_adtstoasc',
             '{}'.format(filename_path),
             ],
            shell=False
        )
        uploads_path.append("{}{}{}.{}".format(DOU_POST_HOST, second_path, filename, "mp4"))
    except:
        raise AssertionError("转换mp4为ts文件失败")

    return uploads_path


def match1(text, *patterns):
    """Scans through a string for substrings matched some patterns (first-subgroups only).

    Args:
        text: A string to be scanned.
        patterns: Arbitrary number of regex patterns.

    Returns:
        When only one pattern is given, returns a string (None if no match found).
        When more than one pattern are given, returns a list of strings ([] if no match found).
    """

    if len(patterns) == 1:
        pattern = patterns[0]
        match = re.search(pattern, text)
        if match:
            return match.group(1)
        else:
            return None
    else:
        ret = []
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                ret.append(match.group(1))
        return ret


def matchall(text, patterns):
    """Scans through a string for substrings matched some patterns.

    Args:
        text: A string to be scanned.
        patterns: a list of regex pattern.

    Returns:
        a list if matched. empty if not.
    """

    ret = []
    for pattern in patterns:
        match = re.findall(pattern, text)
        ret += match

    return ret


# DEPRECATED in favor of get_content()
def get_response(url, faker=False):
    logging.debug('get_response: %s' % url)

    # install cookies
    if cookies:
        opener = request.build_opener(request.HTTPCookieProcessor(cookies))
        request.install_opener(opener)

    if faker:
        response = request.urlopen(
            request.Request(url, headers=fake_headers), None
        )
    else:
        response = request.urlopen(url)

    data = response.read()
    response.data = data
    return response


# DEPRECATED in favor of get_content()
def get_html(url, encoding=None, faker=False):
    content = get_response(url, faker).data
    return str(content, 'utf-8', 'ignore')


# DEPRECATED in favor of get_content()
def get_decoded_html(url, faker=False):
    response = get_response(url, faker)
    data = response.data
    charset = match1(response.headers['content-type'], r'charset=([\w-]+)')
    if charset:
        return data.decode(charset, 'ignore')
    else:
        return data


def get_location(url):
    logging.debug('get_location: {}'.format(url))
    response = session.get(url)
    return response.url


def urlopen_with_retry(*args, method='get', **kwargs):

    retry_time = 3
    for i in range(retry_time):
        try:
            return getattr(requests, method)(
                *args, stream=True, verify=False, **kwargs
            )
        except requests.Timeout as e:
            logging.debug('request attempt {} timeout'.format(str(i + 1)))
            if i + 1 == retry_time:
                raise e
        # try to tackle youku CDN fails
        except requests.HTTPError as http_error:
            logging.debug('HTTP Error with code{}'.format(
                http_error.response.status_code
            ))
            if i + 1 == retry_time:
                raise http_error

        except Exception as e:
            logging.debug("eeeeeee")


def get_content(url, headers=FAKE_HEADERS, charset="utf-8"):
    """Gets the content of a URL via sending a HTTP GET request.

    Args:
        url: A URL.
        headers: Request headers used by the client.

    Returns:
        The content as a string.
    """

    logging.debug('get_content: {}'.format(url))

    if cookies:
        requests.cookies = cookies

    response = urlopen_with_retry(url, headers=headers)
    data = response.content.decode(charset)
    return data


def post_content(url, headers={}, post_data={}, decoded=True, **kwargs):
    """Post the content of a URL via sending a HTTP POST request.

    Args:
        url: A URL.
        headers: Request headers used by the client.
        decoded: Whether decode the response body using UTF-8 or the charset specified in Content-Type.

    Returns:
        The content as a string.
    """
    if kwargs.get('post_data_raw'):
        logging.debug('post_content: %s\npost_data_raw: %s' % (url, kwargs['post_data_raw']))
    else:
        logging.debug('post_content: %s\npost_data: %s' % (url, post_data))

    req = request.Request(url, headers=headers)
    if cookies:
        cookies.add_cookie_header(req)
        req.headers.update(req.unredirected_hdrs)
    if kwargs.get('post_data_raw'):
        post_data_enc = bytes(kwargs['post_data_raw'], 'utf-8')
    else:
        post_data_enc = bytes(parse.urlencode(post_data), 'utf-8')
    response = urlopen_with_retry(req, data=post_data_enc)
    data = response.read()

    # Decode the response body
    if decoded:
        charset = match1(
            response.getheader('Content-Type'), r'charset=([\w-]+)'
        )
        if charset is not None:
            data = data.decode(charset)
        else:
            data = data.decode('utf-8')

    return data


def size_to_mb(size):
    return float("{:.2f}".format(int(size) / 1024 / 1024)) if size is not None else float('inf')


def url_size(url, headers=None, cookies=None):
    headers = get_head(url, headers=headers, cookies=cookies)
    try:
        size = headers["Content-Length"]
        return float("{:.2f}".format(int(size) / 1024 / 1024)) if size is not None else float('inf')
    except KeyError:
        return float('inf')


def urls_size(urls, headers=None):
    return sum([url_size(url, headers=headers, cookies=None) for url in urls])


def url_info(headers, url):
    try:
        size = headers["Content-Length"]
        size = float("{:.2f}".format(int(size) / 1024 / 1024)) if size is not None else float('inf')
    except KeyError:
        size = float('inf')
    try:
        content_type = headers['Content-Type']
    except KeyError:
        content_type = None
    if content_type is not None:
        ext = headers['Content-Type'].split('/')[-1]
    else:
        ext = None

    if not ext:
        ext = re.split(r'\.', url)[-1]
        try:
            ext = re.search(r"(^[a-z]+)[^\w].*$", ext).group(1)
        except AttributeError:
            raise AttributeError("文件类型无法识别")

    return {
        "size": size,
        "ext": ext,
    }


def get_head(url, headers=None, cookies=None):
    logging.debug('get_head: {}'.format(url))
    if cookies:
        session.cookies = cookies
    res = session.head(url, headers=headers)
    if res.status_code != 200:
        res = session.get(url, headers=headers)
    return res.headers


def url_locations(urls, headers=FAKE_HEADERS):
    """

    :param urls: list
    :param headers: FAKE_HEADERS
    :return: list
    """
    locations = []
    for url in urls:
        logging.debug('url_locations: %s' % url)

        response = urlopen_with_retry(url, headers=headers, time=(5, 15))

        locations.append(response.url)
    return locations


def parse_host(host):
    """Parses host name and port number from a string.
    """
    if re.match(r'^(\d+)$', host) is not None:
        return ("0.0.0.0", int(host))
    if re.match(r'^(\w+)://', host) is None:
        host = "//" + host
    o = parse.urlparse(host)
    hostname = o.hostname or "0.0.0.0"
    port = o.port or 0
    return (hostname, port)


def set_proxy(proxy):
    proxy_handler = request.ProxyHandler({
        'http': '%s:%s' % proxy,
        'https': '%s:%s' % proxy,
    })
    opener = request.build_opener(proxy_handler)
    request.install_opener(opener)


def unset_proxy():
    proxy_handler = request.ProxyHandler({})
    opener = request.build_opener(proxy_handler)
    request.install_opener(opener)


# DEPRECATED in favor of set_proxy() and unset_proxy()
def set_http_proxy(proxy):
    if proxy is None:  # Use system default setting
        proxy_support = request.ProxyHandler()
    elif proxy == '':  # Don't use any proxy
        proxy_support = request.ProxyHandler({})
    else:  # Use proxy
        proxy_support = request.ProxyHandler(
            {'http': '%s' % proxy, 'https': '%s' % proxy}
        )
    opener = request.build_opener(proxy_support)
    request.install_opener(opener)


