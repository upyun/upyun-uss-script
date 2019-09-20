#!/usr/bin/env python
# -*- coding: utf-8 -*-
from base64 import b64encode
import requests
import urllib.parse
import os
from copy import deepcopy
from multiprocessing.dummy import Pool as ThreadPool


class QueryUpyun(object):
    def __init__(self, bucket, username, password):
        self.bucket = bucket
        self.username = username
        self.password = password
        self.upyun_api = 'http://v0.api.upyun.com'
        self.dir_list = []

    def _auth(self):
        req_headers = {
            'Authorization': 'Basic ' + b64encode((self.username + ':' + self.password).encode()).decode(),
            'User-Agent': 'up-python-script',
            'X-List-Limit': '300'
        }
        return req_headers

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


class ListFile(QueryUpyun):
    def __init__(self, bucket, username, password):
        super().__init__(username=username, bucket=bucket, password=password)
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def write_file(self, line):
        with open(os.path.join(self.base_dir, '{}_file_list'.format(self.bucket)), 'a') as f:
            f.write(line + '\n')

    def clear_dir(self, path):
        try:
            self.dir_list.remove(path)
        except ValueError:
            pass

    def recursion_filter(self, path, upyun_iter=None):
        file_list = self.read_uss(path, upyun_iter)
        if not file_list:
            self.clear_dir(path)
            return None
        iter = file_list.pop()
        for item in file_list:
            if not item['name']:
                self.clear_dir(path)
                continue
            new_path = path + item['name'] if path == '/' else path + '/' + item['name']
            if item['type'] == 'F':
                self.dir_list.append(new_path)
            else:
                self.write_file(new_path)
        if iter != 'g2gCZAAEbmV4dGQAA2VvZg':
            self.recursion_filter(path, upyun_iter=iter)
        self.clear_dir(path)

    def list_file(self, path):
        self.recursion_filter(path=path)
        while self.dir_list:
            print(self.dir_list)
            pool_v2 = ThreadPool(10)
            pool_v2.map(self.recursion_filter, [path for path in self.dir_list])
            pool_v2.close()
            pool_v2.join()


if __name__ == '__main__':
    query_upyun = ListFile(bucket='', username='', password='')
    path = '/'
    query_upyun.list_file(path)
