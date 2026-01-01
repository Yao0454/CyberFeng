#include <Arduino.h>
#include <WiFi.h>

// ================= 配置区域 =================
// 请在这里填入你的 Wi-Fi 名称和密码
// const char* ssid = "YOUR_WIFI_NAME";     // 你的Wi-Fi名称
// const char* password = "YOUR_WIFI_PASSWORD"; // 你的Wi-Fi密码
const char* ssid = "Wokwi-GUEST";      
const char* password = "";
// ===========================================

void setup() {
  // 1. 初始化串口通信，波特率115200
  Serial.begin(115200);
  
  // 等待一小会儿让串口稳定
  delay(1000);
  Serial.println("\n\nStarting ESP32 Client...");

  // 2. 开始连接 Wi-Fi
  WiFi.mode(WIFI_STA); // 设置为 Station 模式 (客户端模式)
  WiFi.begin(ssid, password);

  Serial.print("Connecting to WiFi");
  
  // 循环等待连接，直到成功
  int retry_count = 0;
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    retry_count++;
    
    // 如果超过 20次 (10秒) 连不上，提示一下
    if(retry_count > 20) {
      Serial.println("\nStill connecting... Check SSID/Password or use 2.4G hotspot.");
      retry_count = 0;
    }
  }

  // 3. 连接成功
  Serial.println("\nSuccess!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP()); // 打印获取到的 IP 地址
}

void loop() {
  // 暂时在主循环里做一个心跳包打印，证明板子没死机
  Serial.println("System alive... (Waiting for Audio logic)");
  delay(5000); // 每5秒打印一次
}


















