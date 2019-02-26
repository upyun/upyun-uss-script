# -*- coding: utf-8 -*-
# 说明
# 使用此脚本需要安装 requests 库，使用pip install requests==2.10.0 安装
# 具体的使用教程，请参考 https://awen.me/archives/801.html 说明
from base64 import b64encode
import requests
import hashlib
import datetime
try:
    import urllib.parse
    # from urllib.parse import quote
    import queue
except ImportError:
    # from urllib import quote
    import Queue as queue
    import urllib
    import sys
    reload(sys)
    sys.setdefaultencoding("utf-8")
# -----------------------
bucket = ''
username = ''
password = ''
path = ''
# -----------------------

queue = queue.LifoQueue()
count = 0


def run(purge):
    date = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
    token = hashlib.md5(password.encode()).hexdigest()
    sign = hashlib.md5((purge + "&" + bucket + "&" +
                        date + "&" + token).encode()).hexdigest()

    Header = {
        "Authorization": 'UpYun ' + bucket + ':' + username + ':' + sign,
        "Date": date,
        "Content-Type": "application/x-www-form-urlencoded",
    }
    try:
        post = urllib.parse.urlencode({'purge': purge})
    except Exception as e:
        post = urllib.urlencode({"purge": purge})
    r = requests.post("http://purge.upyun.com/purge/", post, headers=Header)
    return r.status_code



def do_http_request(method, key, upyun_iter):
    uri = '/' + bucket + (lambda x: x[0] == '/' and x or '/' + x)(key)
    try:
        uri = urllib.parse.quote(uri)
    except Exception as e:
        if isinstance(uri, unicode):
            uri = uri.encode('utf8')
        uri = urllib.quote(uri)
    headers = {}
    headers['Authorization'] = "Basic " + b64encode((username + ':' + password).encode()).decode()
    headers['User-Agent'] = "python3_script_uptechs"
    headers['X-List-Limit'] = '300'
    if upyun_iter is not None or upyun_iter is not 'g2gCZAAEbmV4dGQAA2VvZg':
        headers['x-list-iter'] = upyun_iter

    url = "http://v0.api.upyun.com" + uri
    requests.adapters.DEFAULT_RETRIES = 5
    session = requests.session()
    try:
        response = session.request(method, url, headers=headers, timeout=30)
        status = response.status_code
        if status == 200:
            try:
                content = response.content.decode()
                iter_header = response.headers['x-upyun-list-iter']
            except Exception as e:
                content = response.content
                iter_header = 'g2gCZAAEbmV4dGQAA2VvZg'
            # try:
            #     iter_header = response.headers['x-upyun-list-iter']
            # except Exception as e:
            #     iter_header = 'g2gCZAAEbmV4dGQAA2VvZg'
            return content + "`" + str(iter_header)
        else:
            return None
    except Exception as e:
        pass


def getlist(key, upyun_iter):
    content = do_http_request('GET', key, upyun_iter)
    if not content:
        return None
    content = content.split("`")
    items = content[0].split('\n')
    content = [dict(zip(['name', 'type', 'size', 'time'],
                        x.split('\t'))) for x in items] + content[1].split()
    return content


def print_file_with_iter(path):
    upyun_iter = None
    while True:
        while upyun_iter != 'g2gCZAAEbmV4dGQAA2VvZg':
            res = getlist(path, upyun_iter)
            if res:
                upyun_iter = res[-1]
                for i in res[:-1]:
                    try:
                        if not i['name']:
                            continue
                        new_path = path + i['name'] if path == '/' else path + '/' + i['name']
                        if i['type'] == 'F':
                            queue.put(new_path)
                        elif i['type'] == 'N':

                            url = 'http://' + bucket + '.b0.upaiyun.com' + new_path
                            if run(url) == 200:
                                print(new_path + ' ---> purge success')



                    except Exception as e:
                        print(e)
        else:
            if not queue.empty():
                path = queue.get()
                upyun_iter = None
                queue.task_done()
            else:
                break


if __name__ == '__main__':
    # path = input("input path:")
    print_file_with_iter(path)
    print('刷新全部完成')