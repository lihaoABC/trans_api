import datetime
import pymongo
from app.spider_store.configs import (MONGO_HOST, MONGO_PORT)


class MongoWare(object):

    def __init__(self):

        self.client = pymongo.MongoClient(MONGO_HOST, MONGO_PORT)

        self.db = self.client.URLMsg          # 声明数据库
        self.collection = self.db.urlInfo     # 声明集合

    def info(self, url, message, title=None):
        return {
            "url": url,
            "message": message,
            "tid": datetime.datetime.now().strftime('%Y%m%d%H%M%S%f'),
            "title": title,
            "block": False
        }

    def insert(self, info):

        assert self.collection.insert_one(info), "插入信息失败"

    def exists(self, url):

        return self.collection.find_one({'url': url}) is not None

    def block(self, url):

        info = self.collection.find_one({'url': url})
        if info["block"]:
            return True
        else:
            return False

    def find(self):
        """
        返回
        :return: 前十条数据(可迭代对象mongo.Cursor.cursor)
        """
        # results = self.collection.find().sort('dateId', pymongo.ASCENDING).limit(10)
        return self.collection.find().sort('tid', pymongo.DESCENDING).limit(20)

    def complite(self, url):
        """
        发布成功
        :return:
        """
        condition = {
            "url": url
        }

        info = self.collection.find_one(condition)
        info['block'] = True
        info['tid'] = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
        result = self.collection.update_one(condition, {'$set': info})
        return result.matched_count, result.modified_count

    def update(self, url, message, title=None):
        """
        更新状态信息
        :return: 匹配的数据条数， 影响的数据条数
        """
        condition = {
            "url": url
        }

        info = self.collection.find_one(condition)
        info['message'] = message
        if title is not None:
            info['title'] = title
        info['tid'] = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
        result = self.collection.update_one(condition, {'$set': info})
        return result.matched_count, result.modified_count

    def deleteOne(self, url):
        return self.collection.delete_one({'url': url})

    def deleteMany(self, tid):
        return self.collection.delete_many({'tid': {'$lt': tid}})


if __name__ == '__main__':

    # message = {
    #     "url": "www.baidu.com",
    #     "message": "爬虫开始运行",
    #     "dateId": datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
    # }
    mg = MongoWare()
    # info = mg.info("www.fef.com", "14",)
    # mg.insert(info)
    # info = mg.update("www.baidu.com", "爬虫结束", 'aaa')
    # print(info)
    # 删除
    mg.deleteOne('https://www.bilibili.com/video/av46913509')
    # mg._deleteMany('99999999999999999999')
    results = mg.find()
    for res in results:
        print(res)
    # print(mg._exists('www.baidu.com'))

