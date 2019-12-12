package com.upyun;

import com.upyun.pojo.UpYun;
import com.upyun.utils.HttpPoolUtil;

import java.io.*;
import java.net.URLDecoder;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;


public class ThreadsMove_Copy {

    private static UpYun upYun = new UpYun("", "", "");//填写主要信息
    private static String moveOrCopyTo = ""; //移动到哪个路径
    private static HttpPoolUtil phu = new HttpPoolUtil();

    public static void main(String[] args) throws IOException {
        // 准备数据
        List<String> data = new ArrayList<String>();
        File file = new File(""); //指定本地文件列表位置
        InputStreamReader isr = new InputStreamReader(new FileInputStream(file), StandardCharsets.UTF_8);
        BufferedReader br = new BufferedReader(isr);
        String uri = null;
        while ((uri = br.readLine()) != null) {
            data.add(uri);
        }
        ThreadsMove_Copy threadsMove_copy = new ThreadsMove_Copy();
        threadsMove_copy.handleList(data, 5); //线程数，过大易出现429错误
    }

    /***
     * 线程，可在run()方法中选择 移动还是复制
     */
    static class HandleThread extends Thread {
        private String threadName;
        private List<String> data;
        private int start;
        private int end;

        HandleThread(String threadName, List<String> data, int start, int end) {
            this.threadName = threadName;
            this.data = data;
            this.start = start;
            this.end = end;
        }

        public void run() {
            // TODO 这里处理数据
            List<String> subList = data.subList(start, end)/*.add("^&*")*/;
            System.out.println(threadName + "处理了" + subList.size() + "条！");

            try {
                for (String uri : subList) {
                    //TODO 此处选择 移动还是复制
                    toCopyFile(uri, upYun.getBucket(), moveOrCopyTo);
//                    toMoveFile(uri, upYun.getBucket(), moveOrCopyTo);
                }
            } catch (Exception e) {
                e.printStackTrace();
            }
        }
    }

    /**
     * 多线程处理list
     *
     * @param data      数据list
     * @param threadNum 线程数
     */
    private synchronized void handleList(List<String> data, int threadNum) throws IOException {
        int length = data.size();
        int tl = length % threadNum == 0 ? length / threadNum : (length
                / threadNum + 1);

        for (int i = 0; i < threadNum; i++) {
            int end = (i + 1) * tl;
            HandleThread thread = new HandleThread("线程[" + (i + 1) + "] ", data, i * tl, end > length ? length : end);
            thread.start();
        }
    }

    /***
     * 复制文件
     * @param uri 需要移动的文件URI
     * @param bucket 服务名
     * @param copyTo 复制到哪个URI
     * @throws Exception
     */
    private static void toCopyFile(String uri, String bucket, String copyTo) throws Exception {
        //计算基础签名
        String basicAuth = getBasicAuth(upYun);
        //资源 原uri
        String copySource = "/" + bucket + uri;
        //判断uri是否包含中文
        String regex = "[\u4e00-\u9fa5]";
        Pattern p = Pattern.compile(regex);
        Matcher m = p.matcher(copySource);
        if (m.find()) {
            copySource = chineseEncode(copySource, regex);
        }

        Map<String, String> params = new HashMap<>();
        params.put("X-Upyun-Copy-Source", copySource);
        params.put("Authorization", basicAuth);

        phu.httpSend(uri, copyTo, upYun, params);
    }

    /***
     * 移动文件
     * @param uri 同上
     * @param bucket
     * @param moveTo
     * @throws Exception
     */
    private static void toMoveFile(String uri, String bucket, String moveTo) throws Exception {
        //计算基础签名
        String basicAuth = getBasicAuth(upYun);
        //资源 原uri
        String moveSource = "/" + bucket + uri;
        //判断uri是否包含中文
        String regex = "[\u4e00-\u9fa5]";
        Pattern p = Pattern.compile(regex);
        Matcher m = p.matcher(moveSource);
        if (m.find()) {
            moveSource = chineseEncode(moveSource, regex);
        }

        Map<String, String> params = new HashMap<>();
        params.put("X-Upyun-Move-Source", moveSource);
        params.put("Authorization", basicAuth);
        phu.httpSend(uri, moveTo, upYun, params);
    }

    /***
     * 中文转码
     * @param copySource
     * @param regex
     * @return
     */
    private static String chineseEncode(String copySource, String regex) throws UnsupportedEncodingException {

        List<String> chineseWordsList = new ArrayList<String>();
        Matcher matcher = Pattern.compile(regex).matcher(copySource);
        while (matcher.find()) {
            chineseWordsList.add(matcher.group());
        }

        for (String chineseWord : chineseWordsList) {
            String encode = URLEncoder.encode(chineseWord, "utf-8");
            copySource = copySource.replace(chineseWord, URLDecoder.decode(encode, "latin1"));
        }
        return copySource;
    }

    /***
     * 签名计算
     * @param upYun
     * @return
     * @throws UnsupportedEncodingException
     */
    private static String getBasicAuth(UpYun upYun) throws UnsupportedEncodingException {
        String value = upYun.getOperator()+":"+upYun.getPassword();
        String base64Value = Base64.getEncoder().encodeToString(value.getBytes());
        return "Basic "+base64Value;
    }
}
