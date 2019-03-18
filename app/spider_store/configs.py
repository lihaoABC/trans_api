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
MONGO_HOST = "127.0.0.1"
MONGO_PORT = 27017

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
POST_API = 'http://pcff.dou.gxnews.com.cn/e/admin-92game/newsLogin.php?pw=f3f75a1926949273fe2f9f8c5fac61ab'
POST_HOST = 'http://img.dou.gxnews.com.cn/'
POST_USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                  'Chrome/69.0.3497.100 Safari/537.36'

POST_HEADERS = {
    'user-agent': POST_USER_AGENT,
}


# supported sites
SITES = {
    "baomihua"              : "baomihua",
    'ifeng'                 : 'ifeng',

}

# '163'              : 'netease',
# '56'               : 'w56',
# '365yg'            : 'toutiao',
# 'acfun'            : 'acfun',
# 'archive'          : 'archive',
# 'baidu'            : 'baidu',
# 'bandcamp'         : 'bandcamp',
# 'bigthink'         : 'bigthink',
# 'bilibili'         : 'bilibili',
# 'cctv'             : 'cntv',
# 'cntv'             : 'cntv',
# 'cbs'              : 'cbs',
# 'coub'             : 'coub',
# 'dailymotion'      : 'dailymotion',
# 'douban'           : 'douban',
# 'douyin'           : 'douyin',
# 'douyu'            : 'douyutv',
# 'ehow'             : 'ehow',
# 'facebook'         : 'facebook',
# 'fc2'              : 'fc2video',
# 'flickr'           : 'flickr',
# 'freesound'        : 'freesound',
# 'fun'              : 'funshion',
# 'google'           : 'google',
# 'giphy'            : 'giphy',
# 'heavy-music'      : 'heavymusic',
# 'huomao'           : 'huomaotv',
# 'iask'             : 'sina',
# 'icourses'         : 'icourses',

# 'imgur'            : 'imgur',
# 'in'               : 'alive',
# 'infoq'            : 'infoq',
# 'instagram'        : 'instagram',
# 'interest'         : 'interest',
# 'iqilu'            : 'iqilu',
# 'iqiyi'            : 'iqiyi',
# 'ixigua'           : 'ixigua',
# 'isuntv'           : 'suntv',
# 'iwara'            : 'iwara',
# 'joy'              : 'joy',
# 'kankanews'        : 'bilibili',
# 'khanacademy'      : 'khan',
# 'ku6'              : 'ku6',
# 'kuaishou'         : 'kuaishou',
# 'kugou'            : 'kugou',
# 'kuwo'             : 'kuwo',
# 'le'               : 'le',
# 'letv'             : 'le',
# 'lizhi'            : 'lizhi',
# 'longzhu'          : 'longzhu',
# 'magisto'          : 'magisto',
# 'metacafe'         : 'metacafe',
# 'mgtv'             : 'mgtv',
# 'miomio'           : 'miomio',
# 'mixcloud'         : 'mixcloud',
# 'mtv81'            : 'mtv81',
# 'musicplayon'      : 'musicplayon',
# 'miaopai'          : 'yixia',
# 'naver'            : 'naver',
# '7gogo'            : 'nanagogo',
# 'nicovideo'        : 'nicovideo',
# 'panda'            : 'panda',
# 'pinterest'        : 'pinterest',
# 'pixnet'           : 'pixnet',
# 'pptv'             : 'pptv',
# 'qingting'         : 'qingting',
# 'qq'               : 'qq',
# 'showroom-live'    : 'showroom',
# 'sina'             : 'sina',
# 'smgbb'            : 'bilibili',
# 'sohu'             : 'sohu',
# 'soundcloud'       : 'soundcloud',
# 'ted'              : 'ted',
# 'theplatform'      : 'theplatform',
# 'tiktok'           : 'tiktok',
# 'tucao'            : 'tucao',
# 'tudou'            : 'tudou',
# 'tumblr'           : 'tumblr',
# 'twimg'            : 'twitter',
# 'twitter'          : 'twitter',
# 'ucas'             : 'ucas',
# 'videomega'        : 'videomega',
# 'vidto'            : 'vidto',
# 'vimeo'            : 'vimeo',
# 'wanmen'           : 'wanmen',
# 'weibo'            : 'miaopai',
# 'veoh'             : 'veoh',
# 'vine'             : 'vine',
# 'vk'               : 'vk',
# 'xiami'            : 'xiami',
# 'xiaokaxiu'        : 'yixia',
# 'xiaojiadianvideo' : 'fc2video',
# 'ximalaya'         : 'ximalaya',
# 'yinyuetai'        : 'yinyuetai',
# 'yizhibo'          : 'yizhibo',
# 'youku'            : 'youku',
# 'youtu'            : 'youtube',
# 'youtube'          : 'youtube',
# 'zhanqi'           : 'zhanqi',
# 'zhibo'            : 'zhibo',
# 'zhihu'            : 'zhihu',
