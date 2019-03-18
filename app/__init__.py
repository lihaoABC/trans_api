import logging
from flask import Flask
from logging.handlers import RotatingFileHandler
from configs import (configs, Config)
from celery import Celery
celery = Celery(
        __name__,
        broker=Config.CELERY_BROKER_URL,
        backend=Config.CELERY_RESULT_BACKEND,
        include=['app.spider_store']
    )


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(configs[config_name])
    celery.conf.update(app.config)
    celery.autodiscover_tasks(["app.spider_store"])

    # 注册路由
    from app.modules.index import index_blue
    app.register_blueprint(index_blue)

    from app.modules.download import download_blue
    app.register_blueprint(download_blue)

    return app


def set_logs(config_name):
    # 设置日志的记录等级
    logging.basicConfig(level=configs[config_name].LOG_LEVEL)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)