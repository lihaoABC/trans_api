import json

from flask import render_template, request, jsonify

from app.spider_store.utils.mongo_queue import MongoWare
from app.spider_store.utils.response_code import COD, message_map
from . import index_blue
from app.spider_store.tasks import main


@index_blue.route('/')
def index():
    return render_template('index.html')


@index_blue.route('/download')
def download():
    return render_template('download.html')


@index_blue.route('/trans')
def trans():
    return render_template('trans.html')


@index_blue.route('/transfer', methods=['POST'])
def transfer():
    url = request.form.get("url")
    category = request.form.get("category")
    try:
        main.delay(url, category)
        # main(url, category)
    except AssertionError as e:
        return jsonify({'error': e.__str__()})

    return jsonify({"result": "后台任务开启"})


@index_blue.route('/show', methods=['GET'])
def show_logs():
    mongo = MongoWare()
    mes_list = mongo.find()
    info = []
    for message in mes_list:
        mes_code = message["message"]
        for key, value in COD.__dict__.items():
            if value == mes_code:
                mess = message_map[COD.__dict__[key]]
                message["message"] = mess
                del message["_id"]
                info.append(message)
                break

    return "successCallback"+"("+json.dumps(info)+")"

