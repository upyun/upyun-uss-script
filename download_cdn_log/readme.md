### 依赖
python3

pip install requests

### 使用方法：

python download_cdn_log.py

```
请输入又拍云帐号：test
请输入又拍云帐号密码: test
需要下载日志的域名：test.test.com
下载日志的时间（比如 2019-08-20）：2019-08-20
```

### 结果示例：

```
http://upyun.com/2019-08-20/tp/techs.upyun.com/01_00-techs.upyun.com-8251186865448969771.gz
http://n-log.upyun.com/2019-08-20/tp/techs.upyun.com/02_00-techs.upyun.com-8251186867615106032.gz
http://g.upyun.com/2019-08-20/tp/techs.upyun.com/03_00-techs.upyun.com-8251186869781242293.gz
http://jeyun.com/2019-08-20/tp/techs.upyun.com/05_00-techs.upyun.com-8251186874113514815.gz
http://jeiun.com/2019-08-20/tp/techs.upyun.com/06_00-techs.upyun.com-8251186876279651076.gz
http://jeijg.upyun.com/2019-08-20/tp/techs.upyun.com/08_00-techs.upyun.com-8251186880611923598.gz
http://jeijupyun.com/2019-08-20/tp/techs.upyun.com/10_00-techs.upyun.com-8251186884944196120.gz
```

或者：

```
{} 在 {} 的日志不存在'.format(domain, date)
```