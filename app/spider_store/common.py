# _*_ coding:UTF-8 _*_

import datetime
import io
import os
import random
import re
import sys
import time
import json
import socket
import locale
import logging
import argparse
from http import cookiejar
from importlib import import_module
from urllib import request, parse, error
import urllib3

import requests
from requests.adapters import HTTPAdapter

from app.spider_store.configs import (FAKE_HEADERS, SITES, OUTPUT_DIR, POST_HOST, POST_HEADERS)
from app.spider_store.utils import (log, term, )
from app.spider_store.utils.changeJPG import change_jpg
from app.spider_store.utils.strings import get_filename, unescape_html

# 改变默认编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')

NOT_SITES = {
    '163'              : 'netease',
    '56'               : 'w56',
    '365yg'            : 'toutiao',
    'acfun'            : 'acfun',
    'archive'          : 'archive',
    'baidu'            : 'baidu',
    'bandcamp'         : 'bandcamp',
    'baomihua'         : 'baomihua',
    'bigthink'         : 'bigthink',
    'bilibili'         : 'bilibili',
    'cctv'             : 'cntv',
    'cntv'             : 'cntv',
    'cbs'              : 'cbs',
    'coub'             : 'coub',
    'dailymotion'      : 'dailymotion',
    'douban'           : 'douban',
    'douyin'           : 'douyin',
    'douyu'            : 'douyutv',
    'ehow'             : 'ehow',
    'facebook'         : 'facebook',
    'fc2'              : 'fc2video',
    'flickr'           : 'flickr',
    'freesound'        : 'freesound',
    'fun'              : 'funshion',
    'google'           : 'google',
    'giphy'            : 'giphy',
    'heavy-music'      : 'heavymusic',
    'huomao'           : 'huomaotv',
    'iask'             : 'sina',
    'icourses'         : 'icourses',
    'ifeng'            : 'ifeng',
    'imgur'            : 'imgur',
    'in'               : 'alive',
    'infoq'            : 'infoq',
    'instagram'        : 'instagram',
    'interest'         : 'interest',
    'iqilu'            : 'iqilu',
    'iqiyi'            : 'iqiyi',
    'ixigua'           : 'ixigua',
    'isuntv'           : 'suntv',
    'iwara'            : 'iwara',
    'joy'              : 'joy',
    'kankanews'        : 'bilibili',
    'khanacademy'      : 'khan',
    'ku6'              : 'ku6',
    'kuaishou'         : 'kuaishou',
    'kugou'            : 'kugou',
    'kuwo'             : 'kuwo',
    'le'               : 'le',
    'letv'             : 'le',
    'lizhi'            : 'lizhi',
    'longzhu'          : 'longzhu',
    'magisto'          : 'magisto',
    'metacafe'         : 'metacafe',
    'mgtv'             : 'mgtv',
    'miomio'           : 'miomio',
    'mixcloud'         : 'mixcloud',
    'mtv81'            : 'mtv81',
    'musicplayon'      : 'musicplayon',
    'miaopai'          : 'yixia',
    'naver'            : 'naver',
    '7gogo'            : 'nanagogo',
    'nicovideo'        : 'nicovideo',
    'panda'            : 'panda',
    'pinterest'        : 'pinterest',
    'pixnet'           : 'pixnet',
    'pptv'             : 'pptv',
    'qingting'         : 'qingting',
    'qq'               : 'qq',
    'showroom-live'    : 'showroom',
    'sina'             : 'sina',
    'smgbb'            : 'bilibili',
    'sohu'             : 'sohu',
    'soundcloud'       : 'soundcloud',
    'ted'              : 'ted',
    'theplatform'      : 'theplatform',
    'tiktok'           : 'tiktok',
    'tucao'            : 'tucao',
    'tudou'            : 'tudou',
    'tumblr'           : 'tumblr',
    'twimg'            : 'twitter',
    'twitter'          : 'twitter',
    'ucas'             : 'ucas',
    'videomega'        : 'videomega',
    'vidto'            : 'vidto',
    'vimeo'            : 'vimeo',
    'wanmen'           : 'wanmen',
    'weibo'            : 'miaopai',
    'veoh'             : 'veoh',
    'vine'             : 'vine',
    'vk'               : 'vk',
    'xiami'            : 'xiami',
    'xiaokaxiu'        : 'yixia',
    'xiaojiadianvideo' : 'fc2video',
    'ximalaya'         : 'ximalaya',
    'yinyuetai'        : 'yinyuetai',
    'yizhibo'          : 'yizhibo',
    'youku'            : 'youku',
    'youtu'            : 'youtube',
    'youtube'          : 'youtube',
    'zhanqi'           : 'zhanqi',
    'zhibo'            : 'zhibo',
    'zhihu'            : 'zhihu',
}


dry_run = False
json_output = False
force = False
player = None
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


def get_output_dir():
    return OUTPUT_DIR + datetime.datetime.now().strftime('%Y%m%d') + '/'


def get_output_name():
    return datetime.datetime.now().strftime('%Y%m%d%H%M%S%f') + 'a'


def img_download(image_urls):
    """
    图片下载
    :param image_url: 图片连接
    :return: 上传后的地址列表
    """
    assert image_urls, "图片地址为空"
    new_image_url = []
    # 未能正确获得网页 就进行异常处理
    # res = None
    for image_url in image_urls:
        logging.debug('开始下载: {}'.format(image_url))

        if cookies:
            session.cookies = cookies

        response = urlopen_with_retry(image_url, headers=POST_HEADERS, timeout=(5, 15))
        data = response.content

        img_name = get_output_name()
        image_path = get_output_dir()
        filename = os.path.join(image_path + img_name + '.jpg')
        if re.search(r'gif', image_url):
            filename = os.path.join(image_path + img_name + '.gif')

        if not os.path.isdir(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
        try:
            if data == b'' or None or '':
                logging.debug('内容为空，不执行保存')
                return None
            else:
                with open(filename, 'wb') as f:
                    f.write(data)
                    logging.debug('下载完成\n')
        except:
            logging.debug('下载失败\n')
            return None

        # webp格式转换jpg
        if re.search(r'webp', image_url):
            change_jpg(filename, filename)

        time.sleep(random.random())
        path = datetime.datetime.now().strftime('%Y%m%d') + '/'
        if re.search(r'gif', image_url):
            new_image_url.append(POST_HOST + path + img_name + '.gif')  # 传入上传成功的路径
        else:
            new_image_url.append(POST_HOST + path + img_name + '.jpg')  # 传入上传成功的路径

    return new_image_url


def rc4(key, data):
    # all encryption algo should work on bytes
    assert type(key) == type(data) and type(key) == type(b'')
    state = list(range(256))
    j = 0
    for i in range(256):
        j += state[i] + key[i % len(key)]
        j &= 0xff
        state[i], state[j] = state[j], state[i]

    i = 0
    j = 0
    out_list = []
    for char in data:
        i += 1
        i &= 0xff
        j += state[i]
        j &= 0xff
        state[i], state[j] = state[j], state[i]
        prn = state[(state[i] + state[j]) & 0xff]
        out_list.append(char ^ prn)

    return bytes(out_list)


def general_m3u8_extractor(url, headers={}):
    m3u8_list = get_content(url, headers=headers).split('\n')
    urls = []
    for line in m3u8_list:
        line = line.strip()
        if line and not line.startswith('#'):
            if line.startswith('http'):
                urls.append(line)
            else:
                seg_url = parse.urljoin(url, line)
                urls.append(seg_url)
    return urls


def maybe_print(*s):
    try:
        print(*s)
    except:
        pass


def tr(s):
    if default_encoding == 'utf-8':
        return s
    else:
        return s
        # return str(s.encode('utf-8'))[2:-1]


# DEPRECATED in favor of match1()
def r1(pattern, text):
    m = re.search(pattern, text)
    if m:
        return m.group(1)


# DEPRECATED in favor of match1()
def r1_of(patterns, text):
    for p in patterns:
        x = r1(p, text)
        if x:
            return x


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


def launch_player(player, urls):
    import subprocess
    import shlex
    if (sys.version_info >= (3, 3)):
        import shutil
        exefile=shlex.split(player)[0]
        if shutil.which(exefile) is not None:
            subprocess.call(shlex.split(player) + list(urls))
        else:
            log.wtf('[Failed] Cannot find player "%s"' % exefile)
    else:
        subprocess.call(shlex.split(player) + list(urls))


def parse_query_param(url, param):
    """Parses the query string of a URL and returns the value of a parameter.

    Args:
        url: A URL.
        param: A string representing the name of the parameter.

    Returns:
        The value of the parameter.
    """

    try:
        return parse.parse_qs(parse.urlparse(url).query)[param][0]
    except:
        return None


def unicodize(text):
    return re.sub(
        r'\\u([0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f][0-9A-Fa-f])',
        lambda x: chr(int(x.group(0)[2:], 16)),
        text
    )


# DEPRECATED in favor of util.legitimize()
def escape_file_path(path):
    path = path.replace('/', '-')
    path = path.replace('\\', '-')
    path = path.replace('*', '-')
    path = path.replace('?', '-')
    return path


def ungzip(data):
    """Decompresses data for Content-Encoding: gzip.
    """
    from io import BytesIO
    import gzip
    buffer = BytesIO(data)
    f = gzip.GzipFile(fileobj=buffer)
    return f.read()


def undeflate(data):
    """Decompresses data for Content-Encoding: deflate.
    (the zlib compression is used.)
    """
    import zlib
    decompressobj = zlib.decompressobj(-zlib.MAX_WBITS)
    return decompressobj.decompress(data)+decompressobj.flush()


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
    if response.info().get('Content-Encoding') == 'gzip':
        data = ungzip(data)
    elif response.info().get('Content-Encoding') == 'deflate':
        data = undeflate(data)
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
    charset = r1(r'charset=([\w-]+)', response.headers['content-type'])
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
            return getattr(session, method)(
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


def get_content(url, headers=FAKE_HEADERS):
    """Gets the content of a URL via sending a HTTP GET request.

    Args:
        url: A URL.
        headers: Request headers used by the client.
        decoded: Whether decode the response body using UTF-8 or the charset specified in Content-Type.

    Returns:
        The content as a string.
    """

    logging.debug('get_content: {}'.format(url))

    if cookies:
        session.cookies = cookies

    response = urlopen_with_retry(url, headers=headers)
    data = response.content.decode()
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

    # Handle HTTP compression for gzip and deflate (zlib)
    content_encoding = response.getheader('Content-Encoding')
    if content_encoding == 'gzip':
        data = ungzip(data)
    elif content_encoding == 'deflate':
        data = undeflate(data)

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


def url_size(url, headers=FAKE_HEADERS):
    response = urlopen_with_retry(url, headers=headers)
    size = response.headers['content-length']
    return int(size) if size is not None else float('inf')


def urls_size(urls, headers=FAKE_HEADERS):
    return sum([url_size(url, headers=headers) for url in urls])


def get_head(url, headers=FAKE_HEADERS):
    logging.debug('get_head: {}'.format(url))
    res = urlopen_with_retry(url, headers=headers)
    return res.headers


def url_info(url, headers=FAKE_HEADERS, refer=None):
    logging.debug('url_info: {}'.format(url))
    if refer:
        headers.update({'Referer': refer})
    headers = get_head(url, headers)

    _type = headers['Content-Type']
    if _type == 'image/jpg; charset=UTF-8' or _type == 'image/jpg':
        _type = 'audio/mpeg'  # fix for netease
    mapping = {
        'video/3gpp': '3gp',
        'video/f4v': 'flv',
        'video/mp4': 'mp4',
        'video/MP2T': 'ts',
        'video/quicktime': 'mov',
        'video/webm': 'webm',
        'video/x-flv': 'flv',
        'video/x-ms-asf': 'asf',
        'audio/mp4': 'mp4',
        'audio/mpeg': 'mp3',
        'audio/wav': 'wav',
        'audio/x-wav': 'wav',
        'audio/wave': 'wav',
        'image/jpeg': 'jpg',
        'image/png': 'png',
        'image/gif': 'gif',
        'application/pdf': 'pdf',
    }
    if _type in mapping:
        ext = mapping[_type]
    elif '.' in url:
        _type = ext = url.split('.')[-1]
    else:
        _type = None
        if headers['content-disposition']:
            try:
                filename = parse.unquote(
                    match1(
                        headers['content-disposition'], r'filename="?([^"]+)"?'
                    )
                )
                if len(filename.split('.')) > 1:
                    ext = filename.split('.')[-1]
                else:
                    ext = None
            except Exception:
                ext = None
        else:
            ext = None

    if headers.get('transfer-encoding') != 'chunked':
        size = headers['content-length'] and int(headers['content-length'])
    else:
        size = None

    return _type, ext, size


def url_locations(urls, headers=FAKE_HEADERS):
    locations = []
    for url in urls:
        logging.debug('url_locations: %s' % url)

        response = urlopen_with_retry(url, headers=headers)

        locations.append(response.url)
    return locations


def url_save(
    url, filepath, bar, refer=None, is_part=False, headers=None, timeout=None,
    **kwargs
):
    tmp_headers = headers.copy() if headers else FAKE_HEADERS.copy()
    # When a referer specified with param refer,
    # the key must be 'Referer' for the hack here
    if refer:
        tmp_headers['Referer'] = refer
    file_size = url_size(url, headers=tmp_headers)

    if not os.path.exists(os.path.dirname(filepath)):
        os.mkdir(os.path.dirname(filepath))

    temp_filepath = filepath + '.download' if file_size != float('inf') \
        else filepath
    received = 0
    if not force:
        open_mode = 'ab'

        if os.path.exists(temp_filepath):
            received += os.path.getsize(temp_filepath)
            # if bar:
            #     bar.update_received(os.path.getsize(temp_filepath))
    else:
        open_mode = 'wb'

    if received < file_size:
        if received:
            tmp_headers['Range'] = 'bytes=' + str(received) + '-'
        if refer:
            tmp_headers['Referer'] = refer
        kwargs = {
            'headers': tmp_headers,
        }
        if timeout:
            kwargs['timeout'] = timeout
        response = urlopen_with_retry(url, headers=headers)
        try:
            range_start = int(
                response.headers[
                    'content-range'
                ][6:].split('/')[0].split('-')[0]
            )
            end_length = int(
                response.headers['content-range'][6:].split('/')[1]
            )
            range_length = end_length - range_start
        except Exception:
            content_length = response.headers['content-length']
            range_length = int(content_length) if content_length \
                else float('inf')

        if file_size != received + range_length:
            received = 0
            # if bar:
            #     bar.received = 0
            open_mode = 'wb'

        with open(temp_filepath, open_mode) as output:
            for chunk in response.iter_content(chunk_size=2048):
                if chunk:
                    output.write(chunk)
                    received += len(chunk)
                    # if bar:
                    #     bar.update_received(len(chunk))

    assert received == os.path.getsize(temp_filepath), '{} == {} == {}'.format(
        received, os.path.getsize(temp_filepath), temp_filepath
    )

    if os.access(filepath, os.W_OK):
        # on Windows rename could fail if destination filepath exists
        os.remove(filepath)
    os.rename(temp_filepath, filepath)

    path = POST_HOST + '/'.join(filepath.split('/')[-2:])

    return path


class SimpleProgressBar:
    term_size = term.get_terminal_size()[1]

    def __init__(self, total_size, total_pieces=1):
        self.displayed = False
        self.total_size = total_size
        self.total_pieces = total_pieces
        self.current_piece = 1
        self.received = 0
        self.speed = ''
        self.last_updated = time.time()

        total_pieces_len = len(str(total_pieces))
        # 38 is the size of all statically known size in self.bar
        total_str = '%5s' % round(self.total_size / 1048576, 1)
        total_str_width = max(len(total_str), 5)
        self.bar_size = self.term_size - 28 - 2 * total_pieces_len \
            - 2 * total_str_width
        self.bar = '{:>4}%% ({:>%s}/%sMB) ├{:─<%s}┤[{:>%s}/{:>%s}] {}' % (
            total_str_width, total_str, self.bar_size, total_pieces_len,
            total_pieces_len
        )

    def update(self):
        self.displayed = True
        bar_size = self.bar_size
        percent = round(self.received * 100 / self.total_size, 1)
        if percent >= 100:
            percent = 100
        dots = bar_size * int(percent) // 100
        plus = int(percent) - dots // bar_size * 100
        if plus > 0.8:
            plus = '█'
        elif plus > 0.4:
            plus = '>'
        else:
            plus = ''
        bar = '█' * dots + plus
        bar = self.bar.format(
            percent, round(self.received / 1048576, 1), bar,
            self.current_piece, self.total_pieces, self.speed
        )
        sys.stdout.write('\r' + bar)
        sys.stdout.flush()

    def update_received(self, n):
        self.received += n
        time_diff = time.time() - self.last_updated
        bytes_ps = n / time_diff if time_diff else 0
        if bytes_ps >= 1024 ** 3:
            self.speed = '{:4.0f} GB/s'.format(bytes_ps / 1024 ** 3)
        elif bytes_ps >= 1024 ** 2:
            self.speed = '{:4.0f} MB/s'.format(bytes_ps / 1024 ** 2)
        elif bytes_ps >= 1024:
            self.speed = '{:4.0f} kB/s'.format(bytes_ps / 1024)
        else:
            self.speed = '{:4.0f}  B/s'.format(bytes_ps)
        self.last_updated = time.time()
        self.update()

    def update_piece(self, n):
        self.current_piece = n

    def done(self):
        if self.displayed:
            print()
            self.displayed = False


class PiecesProgressBar:
    def __init__(self, total_size, total_pieces=1):
        self.displayed = False
        self.total_size = total_size
        self.total_pieces = total_pieces
        self.current_piece = 1
        self.received = 0

    def update(self):
        self.displayed = True
        bar = '{0:>5}%[{1:<40}] {2}/{3}'.format(
            '', '=' * 40, self.current_piece, self.total_pieces
        )
        sys.stdout.write('\r' + bar)
        sys.stdout.flush()

    def update_received(self, n):
        self.received += n
        self.update()

    def update_piece(self, n):
        self.current_piece = n

    def done(self):
        if self.displayed:
            print()
            self.displayed = False


class DummyProgressBar:
    def __init__(self, *args):
        pass

    def update_received(self, n):
        pass

    def update_piece(self, n):
        pass

    def done(self):
        pass


def get_output_filename(urls, title, ext, output_dir, merge):
    # lame hack for the --output-filename option
    global output_filename
    if output_filename:
        if ext:
            return output_filename + '.' + ext
        return output_filename

    merged_ext = ext
    if (len(urls) > 1) and merge:
        from .processor.ffmpeg import has_ffmpeg_installed
        if ext in ['flv', 'f4v']:
            if has_ffmpeg_installed():
                merged_ext = 'mp4'
            else:
                merged_ext = 'flv'
        elif ext == 'mp4':
            merged_ext = 'mp4'
        elif ext == 'ts':
            if has_ffmpeg_installed():
                merged_ext = 'mkv'
            else:
                merged_ext = 'ts'
    return '%s.%s' % (title, merged_ext)


def download_urls(
    urls, ext, total_size, output_dir='.', refer=None, merge=True,
    headers=FAKE_HEADERS, **kwargs
):
    assert urls
    if dry_run:
        print('Real URLs:\n{}'.format('\n'.join(urls)))
        return

    if not total_size:
        try:
            total_size = urls_size(urls, headers=headers)
        except:
            import traceback
            traceback.print_exc(file=sys.stdout)
            pass

    title = get_output_name()
    output_filename = get_output_filename(urls, title, ext, output_dir, merge)
    output_filepath = os.path.join(output_dir, output_filename)

    if total_size:
        bar = SimpleProgressBar(total_size, len(urls))
    else:
        bar = PiecesProgressBar(total_size, len(urls))

    if len(urls) == 1:
        url = urls[0]
        print('Downloading %s ...' % tr(output_filename))
        bar.update()
        path = url_save(
            url, output_filepath, bar, refer=refer, headers=headers, **kwargs
        )
        bar.done()
        return path
    else:
        parts = []
        print('Downloading %s.%s ...' % (tr(title), ext))
        bar.update()
        for i, url in enumerate(urls):
            filename = '%s[%02d].%s' % (title, i, ext)
            filepath = os.path.join(output_dir, filename)
            parts.append(filepath)
            # print 'Downloading %s [%s/%s]...' % (tr(filename), i + 1, len(urls))
            bar.update_piece(i + 1)
            url_save(
                url, filepath, bar, refer=refer, is_part=True,
                headers=headers, **kwargs
            )
        bar.done()

        if not merge:
            print()
            return

        if 'av' in kwargs and kwargs['av']:
            from .processor.ffmpeg import has_ffmpeg_installed
            if has_ffmpeg_installed():
                from .processor.ffmpeg import ffmpeg_concat_av
                ret = ffmpeg_concat_av(parts, output_filepath, ext)
                print('Merged into %s' % output_filename)
                if ret == 0:
                    for part in parts:
                        os.remove(part)

        elif ext in ['flv', 'f4v']:
            try:
                from .processor.ffmpeg import has_ffmpeg_installed
                if has_ffmpeg_installed():
                    from .processor.ffmpeg import ffmpeg_concat_flv_to_mp4
                    ffmpeg_concat_flv_to_mp4(parts, output_filepath)
                else:
                    from .processor.join_flv import concat_flv
                    concat_flv(parts, output_filepath)
                print('Merged into %s' % output_filename)
            except:
                raise
            else:
                for part in parts:
                    os.remove(part)

        elif ext == 'mp4':
            try:
                from .processor.ffmpeg import has_ffmpeg_installed
                if has_ffmpeg_installed():
                    from .processor.ffmpeg import ffmpeg_concat_mp4_to_mp4
                    ffmpeg_concat_mp4_to_mp4(parts, output_filepath)
                else:
                    from .processor.join_mp4 import concat_mp4
                    concat_mp4(parts, output_filepath)
                print('Merged into %s' % output_filename)
            except:
                raise
            else:
                for part in parts:
                    os.remove(part)

        elif ext == 'ts':
            try:
                from .processor.ffmpeg import has_ffmpeg_installed
                if has_ffmpeg_installed():
                    from .processor.ffmpeg import ffmpeg_concat_ts_to_mkv
                    ffmpeg_concat_ts_to_mkv(parts, output_filepath)
                else:
                    from .processor.join_ts import concat_ts
                    concat_ts(parts, output_filepath)
                print('Merged into %s' % output_filename)
            except:
                raise
            else:
                for part in parts:
                    os.remove(part)

        else:
            print("Can't merge %s files" % ext)

    print()


def download_rtmp_url(
    url, title, ext, params={}, total_size=0, output_dir='.', refer=None,
    merge=True, faker=False
):
    assert url
    if dry_run:
        print('Real URL:\n%s\n' % [url])
        if params.get('-y', False):  # None or unset -> False
            print('Real Playpath:\n%s\n' % [params.get('-y')])
        return

    if player:
        from .processor.rtmpdump import play_rtmpdump_stream
        play_rtmpdump_stream(player, url, params)
        return

    from .processor.rtmpdump import (
        has_rtmpdump_installed, download_rtmpdump_stream
    )
    assert has_rtmpdump_installed(), 'RTMPDump not installed.'
    download_rtmpdump_stream(url,  title, ext, params, output_dir)


def download_url_ffmpeg(
    url, title, ext, params={}, total_size=0, output_dir='.', refer=None,
    merge=True, faker=False, stream=True
):
    assert url
    if dry_run:
        print('Real URL:\n%s\n' % [url])
        if params.get('-y', False):  # None or unset ->False
            print('Real Playpath:\n%s\n' % [params.get('-y')])
        return

    if player:
        launch_player(player, [url])
        return

    from .processor.ffmpeg import has_ffmpeg_installed, ffmpeg_download_stream
    assert has_ffmpeg_installed(), 'FFmpeg not installed.'

    global output_filename
    if output_filename:
        dotPos = output_filename.rfind('.')
        if dotPos > 0:
            title = output_filename[:dotPos]
            ext = output_filename[dotPos+1:]
        else:
            title = output_filename

    title = tr(get_filename(title))

    ffmpeg_download_stream(url, title, ext, params, output_dir, stream=stream)


def playlist_not_supported(name):
    def f(*args, **kwargs):
        raise NotImplementedError('Playlist is not supported for ' + name)
    return f


def print_info(site_info, title, type, size, **kwargs):

    if type:
        type = type.lower()
    if type in ['3gp']:
        type = 'video/3gpp'
    elif type in ['asf', 'wmv']:
        type = 'video/x-ms-asf'
    elif type in ['flv', 'f4v']:
        type = 'video/x-flv'
    elif type in ['mkv']:
        type = 'video/x-matroska'
    elif type in ['mp3']:
        type = 'audio/mpeg'
    elif type in ['mp4']:
        type = 'video/mp4'
    elif type in ['mov']:
        type = 'video/quicktime'
    elif type in ['ts']:
        type = 'video/MP2T'
    elif type in ['webm']:
        type = 'video/webm'

    elif type in ['jpg']:
        type = 'image/jpeg'
    elif type in ['png']:
        type = 'image/png'
    elif type in ['gif']:
        type = 'image/gif'

    if type in ['video/3gpp']:
        type_info = '3GPP multimedia file (%s)' % type
    elif type in ['video/x-flv', 'video/f4v']:
        type_info = 'Flash video (%s)' % type
    elif type in ['video/mp4', 'video/x-m4v']:
        type_info = 'MPEG-4 video (%s)' % type
    elif type in ['video/MP2T']:
        type_info = 'MPEG-2 transport stream (%s)' % type
    elif type in ['video/webm']:
        type_info = 'WebM video (%s)' % type
    # elif type in ['video/ogg']:
    #    type_info = 'Ogg video (%s)' % type
    elif type in ['video/quicktime']:
        type_info = 'QuickTime video (%s)' % type
    elif type in ['video/x-matroska']:
        type_info = 'Matroska video (%s)' % type
    # elif type in ['video/x-ms-wmv']:
    #    type_info = 'Windows Media video (%s)' % type
    elif type in ['video/x-ms-asf']:
        type_info = 'Advanced Systems Format (%s)' % type
    # elif type in ['video/mpeg']:
    #    type_info = 'MPEG video (%s)' % type
    elif type in ['audio/mp4', 'audio/m4a']:
        type_info = 'MPEG-4 audio (%s)' % type
    elif type in ['audio/mpeg']:
        type_info = 'MP3 (%s)' % type
    elif type in ['audio/wav', 'audio/wave', 'audio/x-wav']:
        type_info = 'Waveform Audio File Format ({})'.format(type)

    elif type in ['image/jpeg']:
        type_info = 'JPEG Image (%s)' % type
    elif type in ['image/png']:
        type_info = 'Portable Network Graphics (%s)' % type
    elif type in ['image/gif']:
        type_info = 'Graphics Interchange Format (%s)' % type
    elif type in ['m3u8']:
        if 'm3u8_type' in kwargs:
            if kwargs['m3u8_type'] == 'master':
                type_info = 'M3U8 Master {}'.format(type)
        else:
            type_info = 'M3U8 Playlist {}'.format(type)
    else:
        type_info = 'Unknown type (%s)' % type

    maybe_print('Site:      ', site_info)
    maybe_print('Title:     ', unescape_html(tr(title)))
    print('Type:      ', type_info)
    if type != 'm3u8':
        print(
            'Size:      ', round(size / 1048576, 2),
            'MiB (' + str(size) + ' Bytes)'
        )
    if type == 'm3u8' and 'm3u8_url' in kwargs:
        print('M3U8 Url:   {}'.format(kwargs['m3u8_url']))
    print()


def mime_to_container(mime):
    mapping = {
        'video/3gpp': '3gp',
        'video/mp4': 'mp4',
        'video/webm': 'webm',
        'video/x-flv': 'flv',
    }
    if mime in mapping:
        return mapping[mime]
    else:
        return mime.split('/')[1]


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


def print_more_compatible(*args, **kwargs):
    import builtins as __builtin__
    """Overload default print function as py (<3.3) does not support 'flush' keyword.
    Although the function name can be same as print to get itself overloaded automatically,
    I'd rather leave it with a different name and only overload it when importing to make less confusion.
    """
    # nothing happens on py3.3 and later
    if sys.version_info[:2] >= (3, 3):
        return __builtin__.print(*args, **kwargs)

    # in lower pyver (e.g. 3.2.x), remove 'flush' keyword and flush it as requested
    doFlush = kwargs.pop('flush', False)
    ret = __builtin__.print(*args, **kwargs)
    if doFlush:
        kwargs.get('file', sys.stdout).flush()
    return ret


def download_main(download, download_playlist, urls, playlist, **kwargs):
    for url in urls:
        if re.match(r'https?://', url) is None:
            url = 'http://' + url

        if playlist:
            download_playlist(url, **kwargs)
        else:
            download(url, **kwargs)


def load_cookies(cookiefile):
    global cookies
    try:
        cookies = cookiejar.MozillaCookieJar(cookiefile)
        cookies.load()
    except Exception:
        import sqlite3
        cookies = cookiejar.MozillaCookieJar()
        con = sqlite3.connect(cookiefile)
        cur = con.cursor()
        try:
            cur.execute("""SELECT host, path, isSecure, expiry, name, value
                        FROM moz_cookies""")
            for item in cur.fetchall():
                c = cookiejar.Cookie(
                    0, item[4], item[5], None, False, item[0],
                    item[0].startswith('.'), item[0].startswith('.'),
                    item[1], False, item[2], item[3], item[3] == '', None,
                    None, {},
                )
                cookies.set_cookie(c)
        except Exception:
            pass
        # TODO: Chromium Cookies
        # SELECT host_key, path, secure, expires_utc, name, encrypted_value
        # FROM cookies
        # http://n8henrie.com/2013/11/use-chromes-cookies-for-easier-downloading-with-python-requests/


def set_socks_proxy(proxy):
    try:
        import socks
        socks_proxy_addrs = proxy.split(':')
        socks.set_default_proxy(
            socks.SOCKS5,
            socks_proxy_addrs[0],
            int(socks_proxy_addrs[1])
        )
        socket.socket = socks.socksocket

        def getaddrinfo(*args):
            return [
                (socket.AF_INET, socket.SOCK_STREAM, 6, '', (args[0], args[1]))
            ]
        socket.getaddrinfo = getaddrinfo
    except ImportError:
        log.w(
            'Error importing PySocks library, socks proxy ignored.'
            'In order to use use socks proxy, please install PySocks.'
        )


def url_to_module(url):

    video_host = r1(r'https?://([^/]+)/', url)
    video_url = r1(r'https?://[^/]+(.*)', url)
    assert video_host and video_url, "The url is wrong."

    if video_host.endswith('.com.cn') or video_host.endswith('.ac.cn'):
        video_host = video_host[:-3]
    domain = r1(r'(\.[^.]+\.[^.]+)$', video_host) or video_host
    assert domain, 'unsupported url: ' + url

    # all non-ASCII code points must be quoted (percent-encoded UTF-8)
    url = ''.join([ch if ord(ch) in range(128) else parse.quote(ch) for ch in url])
    video_host = r1(r'https?://([^/]+)/', url)
    video_url = r1(r'https?://[^/]+(.*)', url)

    k = r1(r'([^.]+)', domain)
    if k in SITES:
        return (
            # import_module('.'.join(['app', 'spider_store', 'extractors', SITES[k]])),
            import_module('app.spider_store.extractors.' + SITES[k]),
            url
        )
    else:
        print('not supported')
        return None, None


def any_download(url, **kwargs):
    m, url = url_to_module(url)
    m.download(url, **kwargs)


def any_download_playlist(url, **kwargs):
    m, url = url_to_module(url)
    m.download_playlist(url, **kwargs)

