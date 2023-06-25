import time
import hashlib
from os.path import join
import config as cfg
import os

def get_app_version():
    import json
    try:
        with open('./version', 'r', encoding='utf8') as f:
            current_version = json.loads(f.read())['version']
    except:
        current_version = ""
    return current_version


def get_model_version():
    return "ChatGLM-6B"


def record_init(cookies):
    '''init cookies and create dir for record'''
    cookies.value.update({'access_time_abs': time.time()})
    cookies.value.update({'access_time': time.strftime("%Y%m%d_%H%M%S", time.localtime(cookies.value['access_time_abs']))})
    cookies.value.update({'hash': hashlib.md5(f"{cookies.value['access_time_abs']}".encode()).hexdigest()})
    cookies.value.update({'dir': join(cfg.PATH_RECORDS, cookies.value['hash'])})
    os.makedirs(cookies.value['dir'], exist_ok=True)
    print(cookies.value)