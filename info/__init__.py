import redis
import logging
from flask import Flask
from logging.handlers import RotatingFileHandler
from configs import configs

redis_store = None


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(configs[config_name])
    global redis_store
    redis_store = redis.StrictRedis(
        host=configs[config_name].REDIS_HOST,
        port=configs[config_name].REDIS_PORT,
        db=configs[config_name].REDIS_DB,
        decode_responses=True)

    # 注册路由
    from info.modules.index import index_blue
    app.register_blueprint(index_blue)

    from info.modules.download import download_blue
    app.register_blueprint(download_blue)

    # 404
    # @app.errorhandler(404)
    # def page_not_found(_):
    #     user = g.user
    #     data = {"user": user.to_dict() if user else None}
    #     return render_template('news/404.html', data=data)

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