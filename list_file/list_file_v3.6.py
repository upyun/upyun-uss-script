#!/usr/bin/env python
# -*- coding: utf-8 -*-
from base64 import b64encode
import requests
import urllib.parse
import os
import time
from copy import deepcopy
from multiprocessing.dummy import Pool as ThreadPool


class QueryUpyun(object):
    def __init__(self, bucket: str, username: str, password: str):
        self.bucket = bucket
        self.username = username
        self.password = password
        self.upyun_api = 'http://v0.api.upyun.com'
        self.max_retry = 3

    def _auth(self) -> dict:
        """
        生成又拍云 REST API 接口的请求头，使用 Basic 验证方式
        :return:
        """
        basic_auth = b64encode((self.username + ':' + self.password).encode()).decode()
        req_headers = {
            'Authorization': 'Basic {}'.format(basic_auth),
            'User-Agent': 'up-python-script',
            'X-List-Limit': '1000',
            'Accept': 'application/json'
        }
        return req_headers

    def read_uss(self, uri: str, upyun_iter: str, retry: int = 0):
        """
        对又拍云 REST API 接口发起 GET 请求
        文档地址：https://help.upyun.com/knowledge-base/rest_api/#e88eb7e58f96e79baee5bd95e69687e4bbb6e58897e8a1a8
        :param uri: 请求的目录
        :param upyun_iter: 分页参数
        :param retry: 重试次数，默认 0 次，最大重试次数为 self.max_retry
        :return: dict
        """
        key = urllib.parse.quote('/' + self.bucket + (lambda x: x[0] == '/' and x or '/' + x)(uri))
        headers = deepcopy(self._auth())
        if upyun_iter and upyun_iter != 'g2gCZAAEbmV4dGQAA2VvZg':
            headers.update({'x-list-iter': upyun_iter})
        url = self.upyun_api + key
        try:
            resp = requests.get(url, headers=headers, timeout=30)
            if resp.status_code == 200:
                content = resp.json()
                try:
                    iter_header = content['iter']
                except KeyError as e:
                    iter_header = 'g2gCZAAEbmV4dGQAA2VvZg'
                items = content['files']
                resp = [{'name': x['name'], 'type': x['type'], 'size': x['length'], 'time': x['last_modified']} for x in
                        items]
                resp.append(iter_header)
                return resp
            else:
                retry += 1
                if retry <= self.max_retry:
                    self.read_uss(uri, upyun_iter, retry=retry)

                print(resp.status_code, resp.json())
                return None
        except Exception as e:
            print(e)
            return None


class ListFile(QueryUpyun):
    def __init__(self, bucket: str, username: str, password: str, detail: bool = False):
        """

        :param bucket: 存储服务名
        :param username: 操作员
        :param password: 操作员密码
        :param detail: 是否显示详细信息：（路径，文件类型，文件大小），默认不显示
        """
        super().__init__(username=username, bucket=bucket, password=password)
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.dir_list = []
        self.detail = detail

    def write_file(self, line, error=False):
        """
        写文件列表到本地文件方法
        if error=True: 记录出现错误的文件目录
        :param line: 文件地址
        :param error: Boolean
        :return: None
        """
        with open(os.path.join(self.base_dir, '{}_file_list.csv'.format(self.bucket)), 'a') as f:
            f.write(line + '\n')
        if error:
            with open(os.path.join(self.base_dir, '{}_error_list.csv'.format(self.bucket)), 'a') as f:
                f.write(line + '\n')

    def clear_dir(self, path):
        """
        删除列表中暂存的目录
        :param path:
        :return:
        """
        try:
            self.dir_list.remove(path)
        except ValueError:
            pass

    def check_old_file_list(self):
        """
        脚本重新执行时，检查是否有老旧文件列表，有就重命名
        :return:
        """
        file_list_path = os.path.join(self.base_dir, '{}_file_list.csv'.format(self.bucket))
        if os.path.exists(file_list_path):
            os.rename(file_list_path, '{}_{}_bak.csv'.format(file_list_path, str(int(time.time()))))

    def list_file(self, dir_name: str, upyun_iter: str = None):
        """
        列文件列表，如果是文件，写入本地；如果是目录，暂存进 self.dir_list
        :param dir_name:
        :param upyun_iter:
        :return:
        """
        file_list = self.read_uss(dir_name, upyun_iter)
        if not file_list:
            self.clear_dir(dir_name)
            self.write_file(dir_name, error=True)
            return None
        iter_str = file_list.pop()
        for item in file_list:
            if not item['name']:
                self.clear_dir(dir_name)
                continue
            new_path = dir_name + item['name'] if dir_name == '/' else dir_name + '/' + item['name']
            if item['type'] == 'folder':
                self.dir_list.append(new_path)
            else:
                if self.detail:
                    line = '{},{},{}'.format(new_path, item['type'], item['size'])
                else:
                    line = new_path
                self.write_file(line)
        return iter_str

    def cycle_filter(self, dir_name: str):
        """
        循环获取分页参数列文件
        :param dir_name: 目录名
        :return:
        """
        iter_str = self.list_file(dir_name)
        while iter_str != 'g2gCZAAEbmV4dGQAA2VvZg':
            iter_str = self.list_file(dir_name, upyun_iter=iter_str)
        self.clear_dir(dir_name)

    def main(self, dir_name: str):
        self.check_old_file_list()
        self.cycle_filter(dir_name=dir_name)
        print('文件列表保存路径在： {}/{}_file_list.csv'.format(self.base_dir, self.bucket))
        print('出错的文件目录保存路径在： {}/{}_error_list.csv'.format(self.base_dir, self.bucket))

        while self.dir_list:
            pool_v2 = ThreadPool(10)
            pool_v2.map(self.cycle_filter, self.dir_list)
            pool_v2.close()
            pool_v2.join()


if __name__ == '__main__':
    # detail 参数默认为 False，如果设置为 True，将列出文件的 `文件路径`，`文件类型`，`文件大小`
    # initial_path 默认为 '/' 从存储根目录开始列文件列表，可以自行指定目录，比如：initial_path = '/tmp', 列出 `/tmp` 路径下面的文件
    query_upyun = ListFile(bucket='', username='', password='', detail=False)
    initial_path = '/'
    query_upyun.main(dir_name=initial_path)
