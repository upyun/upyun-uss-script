package com.upyun.pojo;

public class UpYun {
    private String bucket;
    private String operator;
    private String password;
    private final String url = "http://v0.api.upyun.com";

    public String getBucket() {
        return bucket;
    }

    public void setBucket(String bucket) {
        this.bucket = bucket;
    }

    public String getOperator() {
        return operator;
    }

    public void setOperator(String operator) {
        this.operator = operator;
    }

    public String getPassword() {
        return password;
    }

    public void setPassword(String password) {
        this.password = password;
    }

    public String getUrl() {
        return url;
    }

    public UpYun(String bucket, String operator, String password) {
        this.bucket = bucket;
        this.operator = operator;
        this.password = password;
    }
}
