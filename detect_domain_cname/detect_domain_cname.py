# -*- coding: utf-8 -*-
"""
Created on Wed Oct 17 15:28:34 2018

@author: Stone
@mail support(at)upyun.com

"""

import requests
from dns import resolver
import random
import string
import time


class QueryUpyun(object):
    """
    获取指定帐号下面, 所有的绑定域名
    必需参数:
    account: 又拍云帐号名
    password: 又拍云帐号登录密码
    """

    def __init__(self, account, password):
        self.account = account
        self.password = password
        self.upyun_token_api = 'https://api.upyun.com/oauth/tokens'
        self.upyun_bucket_api = 'http://api.upyun.com/buckets'
        self.name = 'get_domain_list_{}'.format(
            ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4)))
        self.token = self._make_token()
        self.domain_list = list()

    def _make_token(self):
        body = {
            'username': self.account,
            'password': self.password,
            'code': ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(25)),
            'name': self.name,
            'scope': 'global',
            'expired_at': int(time.time()) + 86400  # token 过期时间为 24 小时
        }
        conn = requests.post(self.upyun_token_api, data=body)
        if conn.status_code / 2 == 100:
            return conn.json()['access_token']
        else:
            return None

    def get_domain_name(self, page=None):
        if not self.token:
            return None
        headers = {
            'Authorization': 'Bearer {}'.format(self.token),
            'Content-Type': 'application/json'
        }
        if page:
            conn = requests.get('{}?max={}'.format(self.upyun_bucket_api, page), headers=headers)
        else:
            conn = requests.get(self.upyun_bucket_api, headers=headers)

        for bucket_info in conn.json()['buckets']:
            self.domain_list += [domain_info['domain'] for domain_info in bucket_info['domains']]

        max = conn.json()['pager']['max']
        if max:
            self.get_domain_name(page=max)
        else:
            return [domain for domain in self.domain_list if
                    (domain[-10:] != '.upcdn.net' and domain[-12:] != '.upaiyun.com')]


def detect_dns_resolve(account, password):
    up = QueryUpyun(account=account, password=password)
    domains = up.get_domain_name()
    for domain in domains:
        try:
            cname = resolver.query(domain, 'CNAME')
            for i in cname.response.answer:
                for j in i.items:
                    if j.to_text()[-11:] != '.aicdn.com.':
                        print('{}\t\033[1;35m {} \033[0m'.format(domain, j.to_text()))
                    else:
                        print('{}\t{}'.format(domain, j.to_text()))
        except Exception as e:
            pass


if __name__ == '__main__':
    # 又拍云帐号信息
    #
    account = input('请输入又拍云帐号：')
    password = input('请输入又拍云帐号密码：')
    #
    #
    detect_dns_resolve(account, password)

