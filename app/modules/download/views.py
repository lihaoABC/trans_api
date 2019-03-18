from flask import render_template, request, jsonify
from . import download_blue
# from app.spider_store.crawler import Crawler


# @download_blue.route('/xxx', methods=['POST'])
# def index():
#     url = request.form.get("url")
#     category = request.form.get('category')
#     # r = Crawler(url, category)
#     data = {'url': url, 'category': category}
#     return render_template('trans.html', data=data)