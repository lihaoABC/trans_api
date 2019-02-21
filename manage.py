from flask_script import Manager
from info import create_app, set_logs


app = create_app('development')
manager = Manager(app)
# 配置项目日志
set_logs('development')


if __name__ == '__main__':
    manager.run()