#!/usr/bin/env python
# -*- coding: utf-8 -*-
from base64 import b64encode
import requests
import urllib.parse
import queue
from copy import deepcopy


class QueryUpyun(object):
    def __init__(self, bucket, username, password):
        self.bucket = bucket
        self.username = username
        self.password = password
        self.queue = queue.LifoQueue()
        self.upyun_api = 'http://v0.api.upyun.com'

    def _auth(self):
        req_headers = {
            'Authorization': 'Basic ' + b64encode((self.username + ':' + self.password).encode()).decode(),
            'User-Agent': 'up-python-script',
            'X-List-Limit': '300'
        }
        return req_headers

    def _delete_file(self, uri):
        url = self.upyun_api + urllib.parse.quote('/' + self.bucket + (lambda x: x[0] == '/' and x or '/' + x)(uri))
        headers = deepcopy(self._auth())
        try:
            conn = requests.delete(url, headers=headers)
            if conn.status_code == 200:
                return True
        except requests.exceptions.RequestException as e:
            print(e)
            return None

    def read_uss(self, uri, upyun_iter):
        key = urllib.parse.quote('/' + self.bucket + (lambda x: x[0] == '/' and x or '/' + x)(uri))
        headers = deepcopy(self._auth())
        if upyun_iter and upyun_iter != 'g2gCZAAEbmV4dGQAA2VvZg':
            headers.update({'x-list-iter': upyun_iter})
        url = self.upyun_api + key
        try:
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 200:
                content = response.content.decode()
                try:
                    iter_header = response.headers['x-upyun-list-iter']
                except KeyError as e:
                    iter_header = 'g2gCZAAEbmV4dGQAA2VvZg'
                items = content.split('\n')
                resp = [dict(zip(['name', 'type', 'size', 'time'], x.split('\t'))) for x in items]
                resp.append(iter_header)
                return resp
            else:
                print(response.status_code, response.content)
                return None
        except Exception as e:
            print(e)
            return None

    def recursion_filter(self, path, size, upyun_iter=None):
        file_list = self.read_uss(path, upyun_iter)
        if not file_list:
            return None
        iter = file_list.pop()
        for item in file_list:
            if not item['name']:
                continue
            new_path = path + item['name'] if path == '/' else path + '/' + item['name']
            if item['type'] == 'F':
                self.queue.put(new_path)
            else:
                del_request = self._delete_file(new_path)
                if del_request:
                    with open('deleted_file_list.txt', 'a') as f:
                        f.write(new_path + '\n')
                    print('deleted ----> {}'.format(new_path))
        if iter != 'g2gCZAAEbmV4dGQAA2VvZg':
            self.recursion_filter(path, size, upyun_iter=iter)
        return size

    def delete(self, path):
        file_size = self.recursion_filter(size=0, path=path)
        while not self.queue.empty():
            file_size = self.recursion_filter(size=file_size, path=self.queue.get())
        return True


if __name__ == '__main__':
    query_upyun = QueryUpyun(bucket='', username='', password='')
    path = ''
    query_upyun.delete(path)
