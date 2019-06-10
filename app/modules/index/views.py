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


@index_blue.route('/support')
def support():
    return render_template('tables.html')


@index_blue.route('/support2')
def support2():
    return render_template('tables2.html')


@index_blue.route('/transfer', methods=['POST'])
def transfer():
    url = request.form.get("url")
    category = request.form.get("category")
    username = request.form.get("username")
    # try:
    # main.delay(url, category, username=username, )
    main(url, category, username=username,)
    # except Exception as e:
    #     return jsonify({'error': e.__str__()})

    return jsonify({"result": "后台任务开启"})


@index_blue.route('/show', methods=['GET'])
def show_logs():
    username = request.args.get("username")
    mongo = MongoWare()
    mes_list = mongo.find_by_name(username)
    info = []
    for message in mes_list:
        mes_code = message["message"]
        try:
            mes = int(mes_code)
        except ValueError:
            message["message"] = mes_code
            del message["_id"]
            info.append(message)
            continue
        for key, value in COD.__dict__.items():
            if value == mes_code:
                mess = message_map[COD.__dict__[key]]
                message["message"] = mess
                del message["_id"]
                info.append(message)
                break

    return "successCallback"+"("+json.dumps(info)+")"

