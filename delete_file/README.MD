#### 说明

本脚本适合少量数据单线程删除，超大服务名的数据删除，需要参考脚本和接口进行完善

#### 依赖:
```
python 3
```

```
pip install requests
```

#### 删除指定目录的文件的方法:

在脚本 main 中完善相关参数，其中：

1. bucket：存储服务名
2. username：操作员名
3. password：操作员密码
4. path：需要统计的目录，比如根目录：'/'，img图片目录：'/img'

在脚本中填入上述参数。分别是服务名，操作员名，操作员密码，和待删除的路径。

```
if __name__ == '__main__':
    query_upyun = QueryUpyun(bucket='', username='', password='')
    path = ''
    query_upyun.delete(path)
```

然后 python delete_file.py 进行删除.


#### 后台运行:

1.Centos/RedHad
```
   yum -y install screen
   screen -S delete_upyun_file
   python delete_file.py
```

2.Debian/Ubuntu

```
	sudo apt-get install screen
	screen -S delete_upyun_file
	python delete_file.py
```

通过screen在后台运行脚本的好处就是即使本地与远程ssh主机断开后，程序依然能够正常运行
```
	~$ screen -ls #查看当前后台运行的脚本
	There are screens on:
	        3003.test       (03/24/2016 10:58:26 AM)        (Attached)
	        2860.delete     (03/24/2016 10:57:52 AM)        (Detached)
	        6828.py (03/16/2016 08:50:22 PM)        (Detached)
	3 Sockets in /var/run/screen/S-fangwenjun.
	$ screen -r test #进入已经创建的后台任务中
```



