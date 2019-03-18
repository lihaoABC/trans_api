from importlib import import_module
from app.spider_store.configs import SITES


def import_extractor(k, sites=SITES):
    if k in sites:
        params = import_module('app.spider_store.extractors.'+k)
        return params
    else:
        return "模块不存在"
