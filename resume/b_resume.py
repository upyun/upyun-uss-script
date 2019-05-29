#!/usr/bin/env python
# -*- coding: UTF-8 -*-


'''
Author: WH
Date: 2019-03-22

'''

import hashlib
import requests
import hmac
import base64
import os
import datetime
import time
from threading import Thread

#初始化填写服务名、操作员、操作员密码、本地文件夹路径
#sleep 时间目前默认设置0.3，如果更改建议设置大于0.3

bucket = ''
operator = ''
operator_pd = ''
local_path ='/xxx/xxx/'

api = 'http://v0.api.upyun.com'
method ='PUT'

def gmt_date():
        date = datetime.datetime.utcnow()
        return date.strftime('%a, %d %b %Y %H:%M:%S GMT')
gm_date = gmt_date()

def upload():
        for root,dirs,files in os.walk(local_path):
                root = root
                dirs = dirs
                files = files
                for f in files:
                        url = api + '/' + bucket + '/' + f
                        uri = '/' + bucket + '/' + f
                        path = local_path + f
                        file_size = os.path.getsize(path)
                        def sign(operator,operator_pd,method,uri,gm_date):
                                pd = hashlib.md5(operator_pd.encode('utf-8')).hexdigest()
                                sig = '&'.join([method,uri,gm_date])
                                sign = hmac.new(pd,sig,hashlib.sha1).digest().encode('base64').rstrip()
                                return "UPYUN " + operator + ":" + sign
                        auth = sign(operator,operator_pd,method,uri,gm_date)

                        def read_in_chunk(path,chunk_size = 1024*1024):
                                data = open(path)
                                while True:
                                        chunk_data = data.read(chunk_size)

                                        if not chunk_data:
                                                break
                                        yield chunk_data
                  	
                        headers = {
                                'Authorization':auth,
                                'DATE':gm_date,
                                'x-upyun-multi-disorder':'true',
                                'x-upyun-multi-stage':'initiate',
                                'x-upyun-multi-length':str(file_size),
                                'Content-Length':'0'
                                }
                        r = requests.put(url,data = f,headers = headers)
			#print r.headers
			uuid = r.headers['x-upyun-multi-uuid']
                        if r.status_code == 204:
                                print '******Initate Success******\n'
			else:
				print r.headers['x-upyun-multi-uuid']
                        print('File size:{}\n'.format(file_size))
			print '*******Start Upload******'
			def ch(chunk,id):
				headers = {
					'Authorization':auth,
					'DATE':gm_date,
					'Content-Length':'1048576',
					'x-upyun-multi-stage':'upload',
					'x-upyun-multi-uuid':uuid,
					'x-upyun-part-id':str(id)
					}

				r = requests.put(url,data = chunk,headers = headers)
				if r.status_code // 100 !=2:
					print r.headers
					raise Exception("upload %d get error %d" % (id,r.status_code))
			#	print r.text
			#	print r.headers
				m = (int(headers['x-upyun-part-id']) + 1)*1024*1024
				if file_size < 1048576:
					print ('{0} of {1} bytes read ({2}%)'.format(file_size,file_size,file_size*100/file_size))
				else:
					print('{0} of {1} bytes read ({2}%)'.format(m,file_size,m*100/file_size))
			items=[chunk for chunk in read_in_chunk(path)]
			threads=[]
			for i in range(len(items)):
				id = i
				chunk = items[i]
				t = Thread(target = ch,args = [chunk,id])
				threads.append(t)
			for t in threads:
				t.start()
				time.sleep(0.3)		
			for t in threads:
				t.join()
			print 'stop thread'
                        headers={
                                'Authorization':auth,
                                'DATE':gm_date,
                                'Content-Length':str(0),
                                'x-upyun-multi-stage':'complete',
                                'x-upyun-multi-uuid':uuid
                                }

                        r = requests.put(url,data=f,headers=headers)
			
			if r.status_code // 100 !=2:
				print r.headers
				raise Exception("complete %d get error %s" % (id,r.status_code))
			#print r.text
			#print r.headers
							
if __name__ == "__main__":
        upload()
