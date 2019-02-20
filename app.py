from flask import Flask
from configs import DevelopmentConfig

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
