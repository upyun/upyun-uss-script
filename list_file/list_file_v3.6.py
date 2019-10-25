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
        req_headers = {
            'Authorization': 'Basic ' + b64encode((self.username + ':' + self.password).encode()).decode(),
            'User-Agent': 'up-python-script',
            'X-List-Limit': '1000'
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
                retry += 1
                if retry <= self.max_retry:
                    self.read_uss(uri, upyun_iter, retry=retry)

                print(response.status_code, response.content)
                return None
        except Exception as e:
            print(e)
            return None


class ListFile(QueryUpyun):
    def __init__(self, bucket: str, username: str, password: str):
        super().__init__(username=username, bucket=bucket, password=password)
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.dir_list = []

    def write_file(self, line, error=False):
        """
        写文件列表到本地文件方法
        if error=True: 记录出现错误的文件目录
        :param line: 文件地址
        :param error: Boolean
        :return: None
        """
        with open(os.path.join(self.base_dir, '{}_file_list'.format(self.bucket)), 'a') as f:
            f.write(line + '\n')
        if error:
            with open(os.path.join(self.base_dir, '{}_error_list'.format(self.bucket)), 'a') as f:
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
        file_list_path = os.path.join(self.base_dir, '{}_file_list'.format(self.bucket))
        if os.path.exists(file_list_path):
            os.rename(file_list_path, '{}_{}_bak'.format(file_list_path, str(int(time.time()))))

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
            if item['type'] == 'F':
                self.dir_list.append(new_path)
            else:
                self.write_file(new_path)
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
        print(
            '新开终端输入: \t'
            'tail -f {}/{}_file_list\t'
            '查看文件列表情况\n'.format(self.base_dir, self.bucket)
        )
        print(
            '新开终端输入: \t'
            'tail -f {}/{}_error_list\t'
            '查看出现错误的文件列表\n'.format(self.base_dir, self.bucket)
        )

        while self.dir_list:
            pool_v2 = ThreadPool(10)
            pool_v2.map(self.cycle_filter, self.dir_list)
            pool_v2.close()
            pool_v2.join()


if __name__ == '__main__':
    query_upyun = ListFile(bucket='', username='', password='')
    initial_path = '/'
    query_upyun.main(dir_name=initial_path)
