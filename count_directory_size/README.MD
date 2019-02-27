#### 说明

本脚本适合少量数据统计，超大服务名的统计，需要参考脚本和接口进行完善

####依赖:

```python
sudo pip install requests
```

####统计目录内文件大小的方法:

```python
bucket = ''
username = ''
password = ''

path = ''
```

在脚本中填入上述参数。分别是**服务名**，**操作员名**，**操作员密码**，和**待统计的路径。**

比如:

然后 python count_directory_size.py 进行删除.

#### 其他

脚本运行时间偏长， 建议使用 screen 或者 nohup & 等方式将进程挂起后台执行。



