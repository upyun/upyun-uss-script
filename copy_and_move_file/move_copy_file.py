#-*- coding: utf-8 -*-

import os
import requests
from copy import deepcopy
from base64 import b64encode
from urllib.parse import quote, unquote


class QueryUpyun(object):
	def __init__(self, bucket, username, password):
		self.bucket = bucket
		self.username = username
		self.password = password
		self.upyun_api = 'http://v0.api.upyun.com'
		

	def _Auth(self):
		req_headers = {
			"Authorization": "Basic " + b64encode((self.username + ':' + self.password).encode()).decode(),
			'User-Agent':'Auth-Nie-Python'

		}
		return req_headers

	def req_move_file(self, move_source, move_destination):
		headers = deepcopy(self._Auth())
		headers['X-Upyun-Move-Source'] = ('/' + self.bucket + move_source).encode('utf-8').decode('latin1')
		s = requests.Session()
		key = '/' + self.bucket  + move_destination + move_source

		resp_move = s.put(self.upyun_api + key, headers=headers)
		print("Move " + move_source + " to " + move_destination + move_source)

		if resp_move.status_code != 200:
			with open('move_path_error.txt', 'a') as f:
				f.write(move_source + '\n')

	def req_copy_file(self, copy_source, copy_destination):
		headers = deepcopy(self._Auth())
		headers['X-Upyun-Copy-Source'] = ('/' + self.bucket + copy_source).encode('utf-8').decode('latin1')
		s = requests.Session()
		key = '/' + self.bucket  + copy_destination + copy_source

		resp_copy = s.put(self.upyun_api + key, headers=headers)
		print("Copy " + copy_source + ' to ' + copy_destination + copy_source)

		if resp_copy.status_code != 200:
			with open('copy_path_error.txt', 'a') as f:
				f.write(copy_source +  '\n')
				print(copy_source)



if __name__ == '__main__':
	copy_and_move_init = QueryUpyun('BUCKETNAME', 'OPERATOR', 'OPERATOR_PASSWORD')
	for path in open('LOCAL_FILE_PATH'):
		path = (path.rstrip())
		
		# copy_and_move_init.req_copy_file(path, '/COPYPATH')
		# copy_and_move_init.req_move_file(path, '/MOVEPATH')
	else:
		print("Job is done!")
