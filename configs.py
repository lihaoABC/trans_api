# _*_ coding:utf-8 _*_
import logging


class Config(object):
    pass


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    LOG_LEVEL = logging.ERROR