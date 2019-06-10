# 下载文件保存路径
# OUTPUT_DIR = "/data/videos_store/"
OUTPUT_DIR = "/Users/lihao/Movies/videos_store/"

# redis消息队列配置
REDIS_CONFIG = {
    "host": "localhost",
    "port": 6379,
    "db": 4,
}

# mongoDB日志存储
# MONGO_HOST = "127.0.0.1"
MONGO_HOST = "172.17.0.1"
MONGO_PORT = 27017

# 视频ftp仓库
VIDEO_FTP_HOST = '47.98.221.90'
VIDEO_FTP_PORT = 21
VIDEO_FTP_USER = 'ftpnews'
VIDEO_FTP_PASSWORD = 'video293840'
BUFSIZE = 8192

# 图文ftp仓库

# fake_headers
FAKE_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',  # noqa
    'Accept-Charset': 'UTF-8,*;q=0.5',
    'Accept-Encoding': 'gzip,deflate,sdch',
    'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36',  # noqa
}

# fake_user_agent
FAKE_USER_AGENT = [
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/72.0.3626.96 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:64.0) Gecko/20100101 Firefox/64.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/605.1.15 (KHTML, like Gecko) '
    'Version/12.0.3 Safari/605.1.15',
]


# Publishing interface API

# 豆视频视频发布接口
VIDEO_POST_API = 'http://pcff.dou.gxnews.com.cn/e/admin-92game/newsLogin.php?pw=f3f75a1926949273fe2f9f8c5fac61ab'
# 豆视频图文一键转换接口
DOU_POST_API = 'http://pcff.dou.gxnews.com.cn/e/admin-92game/ecmsdo.php'
# 豆视频文件资源地址
DOU_POST_HOST = 'http://img.dou.gxnews.com.cn/'
# fake_ua
POST_USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                  'Chrome/69.0.3497.100 Safari/537.36'

POST_HEADERS = {
    'user-agent': POST_USER_AGENT,
}


# supported sites
SITES = {
    "baomihua"              : "baomihua",
    'ifeng'                 : 'ifeng',
    'bilibili'              : 'bilibili',
    'acfun'                 : 'acfun',
    'sohu'                  : 'sohu',
    "focus"                 : "sohu",
    'eastday'               : 'eastday',
    'weibo'                 : 'miaopai',
    'qq'                    : 'qq',
    "ku6"                   : 'ku6',
    "btime"                 : "btime",
    "qihoo"                 : "kuaizixun",
    "myzaker"               : "zaker",
    "lieqinews"             : "lieqi",
    "china"                 : "zhonghua",
    "163"                   : "wangyi",
}