# -*- coding: utf-8 -*-
"""
Created on Wed Aug 21 15:28:34 2019
@author: zhanghb
@mail support(at)upai.com

"""

import requests
import random
import string
import time


class QueryUpyun(object):
    """
    获取指定域名中，指定日期的日志
    必需参数:
    account: 又拍云帐号名
    password: 又拍云帐号登录密码
    """

    def __init__(self, account, password):
        self.account = account
        self.password = password
        self.upyun_api = 'https://api.upyun.com'
        self.name = 'get_log_list_{}'.format(
            ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4)))

    def _auth(self):
        body = {
            'username': self.account,
            'password': self.password,
            'code': ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(25)),
            'name': self.name,
            'scope': 'global',
            'expired_at': int(time.time()) + 86400  # token 过期时间为 24 小时
        }
        conn = requests.post('{}/oauth/tokens'.format(self.upyun_api), data=body)
        if conn.status_code / 2 == 100:
            headers = {
                'Authorization': 'Bearer {}'.format(conn.json()['access_token']),
                'Content-Type': 'application/json'
            }
            return headers
        else:
            print(conn.status_code, conn.content)
            return None

    def get_log(self, domain, date):
        conn = requests.get(
            self.upyun_api + '/analysis/archives?domain={}&date={}'.format(domain, date), headers=self._auth())
        log_list = conn.json()['data']
        if not log_list:
            return {'error': '{} 在 {} 的日志不存在'.format(domain, date), 'log': ''}
        return {'error': '', 'log': [log_item['url'] for log_item in log_list]}


if __name__ == '__main__':
    # 又拍云帐号信息
    account = input('请输入又拍云帐号：')
    password = input('请输入又拍云帐号密码：')
    domain = input('需要下载日志的域名：')
    date = input('下载日志的时间（比如 2019-08-20）：')
    #
    up = QueryUpyun(account=account, password=password)
    logs = up.get_log(domain, date)
    print(logs['error']) if logs['error'] else print('\n'.join(logs['log']))
