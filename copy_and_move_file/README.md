java版本 1.8

使用前需要引入pom依赖

````
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
````

填写主要信息

````
UpYun upYun = new UpYun("服务名", "操作员账号", "操作员密码");
String moveOrCopyTo = ""; //移动到哪个路径
File file = new File(""); //指定本地文件列表位置
````

代码**58**行，可切换复制或者移动文件