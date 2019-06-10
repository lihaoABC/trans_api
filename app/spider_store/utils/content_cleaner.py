# -*- coding: UTF-8 -*-
import re

from lxml import html
from lxml.html.clean import Cleaner
from w3lib.html import remove_tags
from bs4 import BeautifulSoup


def cleaner(content_str):
    # 补全标签
    if content_str is None:
        return None
    try:
        soup = BeautifulSoup(content_str, 'lxml')
        html_str = soup.prettify()
    except:
        html_str = content_str

    # 去掉style，scripts
    clean = Cleaner(style=True, scripts=True, comments=True, javascript=True, page_structure=False,
                    safe_attrs_only=False)
    tree = html.fromstring(html_str)
    content = html.tostring(clean.clean_html(tree), encoding='UTF-8')

    # 删除其他标签，只保留p与img
    con = remove_tags(content, keep=('img', 'p'))

    # 去掉空格，换行
    enter = re.compile('\n')
    con = enter.sub('', con).replace(' ', '')

    # 清理img其他属性
    img_attr1 = re.compile(r'<img(.*?)src')
    con = img_attr1.sub('<img src', con)

    img_attr3 = re.compile(r'<img(.*?)data-original', re.S)
    con = img_attr3.sub('<img src', con)

    try:
        img_attr2 = re.findall(r'src=".*?"(.*?)>', con)
        for attr in img_attr2:
            con = con.replace(attr, '')
    except:
        pass

    # 清理p标签
    p_class = re.compile(r'<p(.*?)>')
    con = p_class.sub('<p>', con)

    # 删除空的p标签
    con = con.replace(r'<p></p>', '')

    # 删除img外围的p标签
    imgs = re.findall(r'<img[^>]+>', con, re.S)
    for img in imgs:
        try:
            con = con.replace('<p>' + img + '</p>', img)
        except Exception as e:
            pass

    # 国际在线站点文章末尾清理
    p_last = re.compile(r'>标签：.*')
    con = p_last.sub('>', con)

    return con


def content_processing(content, image_paths):
    # 正文内容处理
    regex1 = re.compile(r'src="(.*?)"')
    old_paths = regex1.findall(content)
    for i in range(len(old_paths)):
        try:
            content = content.replace(old_paths[i], image_paths[i])
        except Exception:
            raise Exception('图片下载不全，发布失败')

    # 分页
    regex2 = re.compile(r'<img src=".*?">')
    img = regex2.findall(content)
    for i in range(len(img)):
        if ((i + 1) % 3 == 0) and (i != 0) and (i != len(img) - 1):
            content = content.replace(img[i], img[i] + "[!--empirenews.page--]")

    # 去除文章内容中的空格
    content = re.sub(r"\s*", '', content)
    content = re.sub(r"src", ' src', content)

    return content
