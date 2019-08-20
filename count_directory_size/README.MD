#### 说明

本脚本适合少量数据统计，超大服务名的统计，需要参考脚本和接口进行完善

####依赖:
```
python 3
```

```
pip install requests
```

####统计目录内文件大小的方法:

在脚本 main 中完善相关参数，其中：

1. bucket：存储服务名
2. username：操作员名
3. password：操作员密码
4. path：需要统计的目录，比如根目录：'/'，img图片目录：'/img'


```
if __name__ == '__main__':
    query_upyun = QueryUpyun(bucket='', username='', password='')
    path = ''
    dir_size = query_upyun.count(path)
    print('total {} GB'.format(dir_size))
```



然后 python count_directory_size.py 运行脚本

#### 其他

脚本运行时间偏长， 建议使用 screen 或者 nohup & 等方式将进程挂起后台执行。



