from flask_script import Manager
from app import create_app, set_logs
from flask_cors import CORS


app = create_app('development')
CORS(app)
manager = Manager(app)
# 配置项目日志
set_logs('development')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    # manager.run()
