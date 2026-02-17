#include <Arduino.h>
#include <TFT_eSPI.h>
#include <XPT2046_Touchscreen.h>
#include <lvgl.h>
#include <ArduinoJson.h>

// 导入你的模块
#include "webcom.h"
#include "ui_manager.h"

// --- 硬件引脚定义 ---
#define XPT2046_CS 33
#define XPT2046_CLK 25
#define XPT2046_MISO 39
#define XPT2046_MOSI 32

// --- 全局对象 ---
TFT_eSPI tft = TFT_eSPI();
SPIClass touchSpi = SPIClass(VSPI);
XPT2046_Touchscreen ts(XPT2046_CS); // 软件轮询模式

// 你的功能模块实例化
UIManager ui;
WebCom web("http://129.212.226.20:1111"); // Python 后端地址

// --- LVGL 驱动接口 (必须留在 main 或驱动层) ---

void my_disp_flush(lv_disp_drv_t *disp, const lv_area_t *area, lv_color_t *color_p) {
    uint32_t w = (area->x2 - area->x1 + 1);
    uint32_t h = (area->y2 - area->y1 + 1);
    tft.startWrite();
    tft.setAddrWindow(area->x1, area->y1, w, h);
    tft.pushColors((uint16_t *)&color_p->full, w * h, true);
    tft.endWrite();
    lv_disp_flush_ready(disp);
}

void my_touchpad_read(lv_indev_drv_t *indev_driver, lv_indev_data_t *data) {
    if (ts.touched()) {
        TS_Point p = ts.getPoint();
        // 使用你之前调通的过滤逻辑
        if (p.z > 4000 || p.z < 200 || p.x == 0 || p.y == 0) {
            data->state = LV_INDEV_STATE_REL;
            return;
        }
        data->point.x = map(p.x, 200, 3800, 0, 320);
        data->point.y = map(p.y, 200, 3800, 0, 240);
        data->state = LV_INDEV_STATE_PR;
    } else {
        data->state = LV_INDEV_STATE_REL;
    }
}

// --- 核心业务逻辑：当 UI 按钮被点击时执行 ---

void onFetchData() {
    ui.addLog(">> Sending Command...");
    
    // 1. 调用你的 Python 后端 /control 接口 (因为它返回 JSON)
    // 注意：/chat 返回的是音频流，ESP32 无法直接作为 JSON 解析，会崩溃
    String response = web.sendGetRequest("/control?command=restart");
    
    Serial.println("Response: " + response);

    // 2. 解析 JSON 结果
    StaticJsonDocument<512> doc;
    DeserializationError error = deserializeJson(doc, response);

    if (error) {
        ui.updateServerStatus("Parse Err", false);
        ui.addLog("X JSON Decode Failed");
        return;
    }

    // 3. 安全提取字段 (对应你 Python 中的 {"status": "success", "message": "..."})
    const char* status = doc["status"] | "failed";
    const char* msg = doc["message"] | doc["detail"] | "No msg";

    // 4. 更新模块化的 UI
    bool isOk = (strcmp(status, "success") == 0);
    ui.updateServerStatus(status, isOk);
    ui.addLog(msg);
}

void on_refresh_timer(lv_timer_t* timer) {
    if(!web.isConnected()) return;

    String json = web.sendGetRequest("/status");
    StaticJsonDocument<256> doc;
    deserializeJson(doc, json);

    if (doc.containsKey("model_status")) {
        const char* m_status = doc["model_status"] | "Offline";
        ui.updateServerStatus(m_status, true);
    }
}


// --- 初始化 ---

void setup() {
    Serial.begin(115200);

    // 1. 硬件初始化
    tft.init();
    tft.setRotation(1);

    tft.fillScreen(TFT_BLACK);
    pinMode(21, OUTPUT);
    analogWrite(21, 255); 

    touchSpi.begin(XPT2046_CLK, XPT2046_MISO, XPT2046_MOSI, XPT2046_CS);
    ts.begin(touchSpi);
    ts.setRotation(1);

    // 2. LVGL 核心初始化
    lv_init();
    static lv_disp_draw_buf_t draw_buf;
    static lv_color_t buf[320 * 10];
    lv_disp_draw_buf_init(&draw_buf, buf, NULL, 320 * 10);

    static lv_disp_drv_t disp_drv;
    lv_disp_drv_init(&disp_drv);
    disp_drv.hor_res = 320;
    disp_drv.ver_res = 240;
    disp_drv.flush_cb = my_disp_flush;
    disp_drv.draw_buf = &draw_buf; // 注意 &
    lv_disp_drv_register(&disp_drv);

    static lv_indev_drv_t indev_drv;
    lv_indev_drv_init(&indev_drv);
    indev_drv.type = LV_INDEV_TYPE_POINTER;
    indev_drv.read_cb = my_touchpad_read;
    lv_indev_drv_register(&indev_drv);

    // 3. 模块初始化
    ui.init();
    ui.setOnBtnClick(onFetchData);

    lv_timer_create(on_refresh_timer, 5000, NULL);

    // 4. 联网
    ui.addLog("Connecting to WiFi...");
    web.connectWiFi("CMCC-301", "15926081964");
    
    if(web.isConnected()) {
        ui.updateServerStatus("WiFi OK", true);
        ui.addLog("WiFi Connected!");
    } else {
        ui.updateServerStatus("No WiFi", false);
    }
}

void loop() {
    // 运行 LVGL 定时器
    lv_timer_handler();
    delay(5);
}