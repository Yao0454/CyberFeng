#ifndef WEBCOM_H
#define WEBCOM_H

#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

class WebCom {
private:
    const char* serverUrl;

public:
    // 构造函数 传一个服务器的基础地址
    WebCom(const char* _serverUrl);

    // 初始化 WiFi
    void connectWiFi(const char* ssid, const char* password);
    bool isConnected();

    // 发送 GET 请求并返回结果
    // 我们可以选择使用回调函数或者是返回字符串
    String sendGetRequest(const char* endpoint);

    // 发送 POST 请求
    String sendPostRequest(const char* endpoint, String jsonpayload);

};

#endif
