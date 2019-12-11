package com.upyun.utils;

import com.upyun.pojo.UpYun;
import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.apache.http.client.config.RequestConfig;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpPut;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClientBuilder;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.impl.conn.PoolingHttpClientConnectionManager;

import java.net.URLDecoder;
import java.net.URLEncoder;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * 连接池工具类
 */
public class HttpPoolUtil {
    private static Log logger = LogFactory.getLog(HttpPoolUtil.class);

    private static final String UTF8 = "UTF-8";
    private static volatile boolean isClosed = false;

    private static final int maxTotalPool = 10000;
    private static final int MAX_TIMEOUT = 5000;
    private static final int RequestTimeout = 2000;

    private static RequestConfig requestConfig;
    private static HttpClientBuilder httpClientBuilder;
    private static PoolingHttpClientConnectionManager poolConnManager;


    static {
        // 设置连接池
        poolConnManager = new PoolingHttpClientConnectionManager();
        poolConnManager.setMaxTotal(maxTotalPool);//设置连接池大小
        poolConnManager.setDefaultMaxPerRoute(maxTotalPool);

        RequestConfig.Builder configBuilder = RequestConfig.custom();
        // 设置连接超时
        configBuilder.setConnectTimeout(MAX_TIMEOUT);
        // 设置读取超时
        configBuilder.setSocketTimeout(MAX_TIMEOUT);
        // 设置从连接池获取连接实例的超时
        configBuilder.setConnectionRequestTimeout(RequestTimeout);
        // 在提交请求之前 测试连接是否可用
        //configBuilder.setStaleConnectionCheckEnabled(true);
        requestConfig = configBuilder.build();
        //
        httpClientBuilder = HttpClients.custom().setConnectionManager(poolConnManager).setDefaultRequestConfig(requestConfig);
        System.out.println(">>>>>>>>>>> PoolingHttpClientConnectionManager初始化成功 >>>>>>>>>>>");
    }

    public void httpSend(String uri, String moveOrCopyTo, UpYun upYun, Map<String,String> params) throws Exception {
        //这里的uri需要填写 被移动后的uri路径
        String finalUri = "/" + upYun.getBucket() + moveOrCopyTo + uri;

        CloseableHttpClient httpClient = HttpPoolUtil.getHttpClient();

        //请求的接口
        HttpPut httpPut = new HttpPut(upYun.getUrl() + finalUri);

        if (!params.isEmpty()){
            for (String key : params.keySet()) {
                httpPut.setHeader(key,params.get(key));
            }
        }

//        httpPut.setHeader("Content-Length","0");
//        httpPut.setHeader("Date", date);
        CloseableHttpResponse execute = httpClient.execute(httpPut);
        System.out.println(execute);
//        httpClient.close();
    }

    /**
     * 获取HttpClient客户端
     *
     * @return httpClient
     */
    public static CloseableHttpClient getClient() {
        CloseableHttpClient httpClient = HttpClients.custom()
                .setConnectionManager(poolConnManager)
                .setDefaultRequestConfig(requestConfig)
                .build();
        if (null == httpClient) {
            httpClient = HttpClients.createDefault();
        }

        return httpClient;
    }

    /**
     * 从http连接池里获取客户端实例
     *
     * @return httpClient
     */
    public static CloseableHttpClient getHttpClient() {
        CloseableHttpClient httpClient = httpClientBuilder.build();
        if (null == httpClient) {
            logger.info("---------HttpClients.createDefault()---------");
            httpClient = HttpClients.createDefault();
        }
        return httpClient;
    }

    /**
     * 关闭连接池资源
     */
    public static void closePool() {
        if (!isClosed) {
            isClosed = true;
            poolConnManager.close();
        }
    }

}
