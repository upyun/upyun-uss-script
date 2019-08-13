建议使用 python 3 环境

依赖 requests：

```
pip install requests
```

使用方法：

直接执行这个pytohn 脚本文件，输入又拍云登录名和登录密码就能列出绑定在这个帐号下面的所有域名。

```
$ python list_domain/list_domain.py

请输入又拍云帐号：techs-test
请输入又拍云帐号密码：------

support.upyun.com
kefu.upyun.com
ykf.yupoo.com
push.frankyapilivetest5.v5linux.com
pull.frankyapilivetest5.v5linux.com
push.frankyapilivetest4.v5linux.com
pull.frankyapilivetest4.v5linux.com
rtmp.v5linux.com
zhanghb.b1.v5linux.com
zhanghb.b0.v5linux.com
techs.upyun.com

```