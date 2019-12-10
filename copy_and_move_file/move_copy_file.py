#-*- coding: utf-8 -*-

import os
import requests
from copy import deepcopy
from base64 import b64encode
from urllib.parse import quote, unquote


class QuertUpyun(object):
	def __init__(self, bucket, username, password):
		self.bucket = bucket
		self.username = username
		self.password = password
		self.upyun_api = 'http://v0.api.upyun.com'
		

	def _auth(self):
		req_headers = {
			"Authorization": "Basic " + b64encode((self.username + ':' + self.password).encode()).decode(),
			'User-Agent':'Auth-Nie-Python'
			# 'Content-Length':'0'
		}
		return req_headers

	def reqMoveFile(self, move_source, move_destination):
		headers = deepcopy(self._auth())
		headers['X-Upyun-Move-Source'] = ('/' + self.bucket + move_source).encode('utf-8').decode('latin1')
		s = requests.Session()
		key = '/' + self.bucket  + move_destination + move_source

		r = s.put(self.upyun_api + key, headers=headers)
		print(r.status_code)
		print(r.headers)

	def reqCopyFile(self, copy_source, copy_destination):
		headers = deepcopy(self._auth())
		headers['X-Upyun-Copy-Source'] = ('/' + self.bucket + copy_source).encode('utf-8').decode('latin1')
		s = requests.Session()
		key = '/' + self.bucket  + copy_destination + copy_source
		# key = unquote('/' + self.bucket  + copy_destination + copy_source)

		respCopy = s.put(self.upyun_api + key, headers=headers)
		# print(respCopy.requests.headers)
		print(respCopy.url)
		print(respCopy.status_code)
		# print(respCopy.request.headers)

if __name__ == '__main__':
	q = QuertUpyun('', '', '')
	# for i in open('file_list.txt'):
	for i in open(''):
		i = (i.rstrip())
		q.reqCopyFile(i, '')
		# q.reqMoveFile(i, 'move_to_folder')
