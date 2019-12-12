java版本 1.8

使用脚本前需要引入依赖

```xml
<dependency>
    <groupId>org.apache.httpcomponents</groupId>
    <artifactId>httpclient</artifactId>
    <version>4.5.2</version>
</dependency>

<dependency>
    <groupId>com.alibaba</groupId>
    <artifactId>fastjson</artifactId>
    <version>1.2.58</version>
</dependency>
```

需要修改参数

```
UpYun upYun = new UpYun("服务名", "操作员账号", "操作员密码");
String moveOrCopyTo = ""; //填写要移动到哪个路径
```

线程数修改

```
threadsMove_copy.handleList(data, 5); //线程数，当前设置为5个线程，过高易造成429错误
```

代码 **58** 行可以切换复制和移动文件方法