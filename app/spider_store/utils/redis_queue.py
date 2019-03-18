import redis
import hashlib
import datetime
from app.spider_store.configs import REDIS_CONFIG


class RedisQueue(object):

    def __init__(self):
        """连接redis"""
        pool = redis.ConnectionPool(**REDIS_CONFIG)
        self.pool = pool
        self.redis = redis.StrictRedis(connection_pool=pool)

    def score(self):
        return int(datetime.datetime.now().strftime('%Y%m%d'))

    def url_sha1(self, key):
        """sha1加密"""
        url_sha1 = hashlib.sha1(key.encode()).hexdigest()
        return url_sha1

    def add_first(self, url):
        """首次向redis中添加String"""
        sha1 = self.url_sha1(url)
        assert self.redis.set(sha1, self.score(), nx=True), '此URL重复'

    def add(self, url, message):
        """更新String信息"""
        sha1 = self.url_sha1(url)
        assert self.redis.set(sha1, message, xx=True), "此URL不存在"

    def delete(self, url):
        """删除该条信息"""
        sha1 = self.url_sha1(url)
        assert self.redis.delete(sha1), "删除失败"

    def finish(self, sha1):
        """爬取成功"""
        assert self.redis.set(sha1, self.score(), xx=True), "此URL不存在"

    def queried(self, url):
        """查询当前url状态信息"""
        sha1 = self.url_sha1(url)
        try:
            return self.redis.get(sha1)
        except Exception:
            raise Exception("查询失败")



if __name__ == '__main__':
    rd = RedisQueue()
    # rd.add_first('www.baidus.com')
    print(int(rd.queried('www.baidus.com')))