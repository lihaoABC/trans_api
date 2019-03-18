# _*_ coding:utf-8 _*_
import logging


class Config(object):
    """工程信息配置"""


    # redis数据库
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379
    REDIS_DB = 5

    # celery配置
    CELERY_BROKER_URL = 'redis://localhost:6379/6'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/7'

    # 默认日志等级
    LOG_LEVEL = logging.DEBUG


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    LOG_LEVEL = logging.ERROR


configs = {
    "development": DevelopmentConfig,
    "production": ProductionConfig
}