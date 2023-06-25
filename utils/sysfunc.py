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
    return "ChatGLM2-6B"


def record_init(cookies):
    '''init cookies and create dir for record'''
    cookies.value.update({'access_time_abs': time.time()})
    cookies.value.update({'access_time': time.strftime("%Y%m%d_%H%M%S", time.localtime(cookies.value['access_time_abs']))})
    cookies.value.update({'hash': hashlib.md5(f"{cookies.value['access_time_abs']}".encode()).hexdigest()})
    cookies.value.update({'dir': join(cfg.PATH_RECORDS, cookies.value['hash'])})
    cookies.value.update({'dir_docx_generated': join(cookies.value['dir'], f"考察报告_{cookies.value['access_time']}.docx")})
    os.makedirs(cookies.value['dir'], exist_ok=True)
    print(cookies.value)
    print('cookies init done')
    print('------------------')
    
    
def parse_text(text):
    """copy from https://github.com/GaiZhenbiao/ChuanhuChatGPT/"""
    lines = text.split("\n")
    lines = [line for line in lines if line != ""]
    count = 0
    for i, line in enumerate(lines):
        if "```" in line:
            count += 1
            items = line.split('`')
            if count % 2 == 1:
                lines[i] = f'<pre><code class="language-{items[-1]}">'
            else:
                lines[i] = f'<br></code></pre>'
        else:
            if i > 0:
                if count % 2 == 1:
                    line = line.replace("`", "\`")
                    line = line.replace("<", "&lt;")
                    line = line.replace(">", "&gt;")
                    line = line.replace(" ", "&nbsp;")
                    line = line.replace("*", "&ast;")
                    line = line.replace("_", "&lowbar;")
                    line = line.replace("-", "&#45;")
                    line = line.replace(".", "&#46;")
                    line = line.replace("!", "&#33;")
                    line = line.replace("(", "&#40;")
                    line = line.replace(")", "&#41;")
                    line = line.replace("$", "&#36;")
                lines[i] = "<br>"+line
    text = "".join(lines)
    return text
