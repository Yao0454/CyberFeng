#include <Arduino.h>
#include <TFT_eSPI.h>
#include <XPT2046_Touchscreen.h>
#include <cstring>
#include <lvgl.h>
#include <ArduinoJson.h>

// 导入你的模块
#include "ArduinoJson/Document/StaticJsonDocument.hpp"
#include "ArduinoJson/Json/JsonSerializer.hpp"
#include "freertos/portmacro.h"
#include "freertos/projdefs.h"
#include "webcom.h"
#include "ui_manager.h"

// FreeRTOS 多线程
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#include <freertos/semphr.h>
#include <freertos/queue.h>

// 硬件引脚定义
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

// FreeRTOS 句柄
SemaphoreHandle_t lvgl_mutex;
QueueHandle_t chat_queue;

// LVGL 驱动接口

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


// 业务逻辑：处理按钮指令
void handleCommand(const char* cmd) {
    ui.addLog(String(">> Executing: " + String(cmd)).c_str());
    if (strcmp(cmd, "RESTART") == 0) {
        web.sendGetRequest("/control?command=restart");
    } else if (strcmp(cmd, "FETCH") == 0) {
        // 手动刷新逻辑
    }
}

// 业务逻辑：处理权重切换
void handleWeight(const char* weight) {
    ui.addLog(String(">> Changing Weight: " + String(weight)).c_str());
    web.sendGetRequest("/set_gpt_weights?weights_path=" + String(weight));
}

void handlChatSubmit(const char* msg) {
    char buf[128];
    strncpy(buf, msg, sizeof(buf) - 1);
    buf[sizeof(buf) - 1] = '\0';

    xQueueSend(chat_queue, &buf, 0);
}

// FreeRTOS 任务
void TaskUI(void *pvParameters) {
    while(1) {
        if (xSemaphoreTake(lvgl_mutex, portMAX_DELAY)) {
            lv_timer_handler();
            xSemaphoreGive(lvgl_mutex);
        }
        vTaskDelay(pdMS_TO_TICKS(5));
    }
}

void TaskBackend(void *pvParameters) {

    char msg_buf[128];
    TickType_t last_status_time = 0;
    const TickType_t status_interval = pdMS_TO_TICKS(5000);

    while(1) {
        if (web.isConnected()) {
            // 优先处理聊天队列
            if (xQueueReceive(chat_queue, &msg_buf, pdMS_TO_TICKS(100)) == pdTRUE) {
                StaticJsonDocument<256> doc;
                doc["message"] = msg_buf;
                String payload;
                serializeJson(doc, payload);

                String response = web.sendPostRequest("/text", payload);

                StaticJsonDocument<256> res_doc;
                if (deserializeJson(res_doc, response) == DeserializationError::Ok) {
                    const char* reply = res_doc["reply"] | "Error";
                    if (xSemaphoreTake(lvgl_mutex, portMAX_DELAY)) {
                        ui.addChatMessage("CyberFeng", reply);
                        xSemaphoreGive(lvgl_mutex);
                    }
                }
            }

            if (xTaskGetTickCount() - last_status_time >=  status_interval) {
                // 后台执行 HTTP 请求， 不阻塞 UI
                last_status_time = xTaskGetTickCount();
                String json = web.sendGetRequest("/status");
                StaticJsonDocument<256> doc;
                if (deserializeJson(doc, json) == DeserializationError::Ok) {
                    float cpu = doc["cpu"] | 0.0f;
                    const char* model = doc["model"] | "CyberFeng";

                    // 安全更新 UI
                    if (xSemaphoreTake(lvgl_mutex, portMAX_DELAY)) {
                        ui.updateStats(cpu, 0, model);
                        if (doc.containsKey("latest_msg")) {
                            const char* msg = doc["latest_msg"];
                            ui.addChatMessage("System", msg);
                        }

                        xSemaphoreGive(lvgl_mutex);
                    }
                }
            }
        } else {
            vTaskDelay(pdMS_TO_TICKS(500));
        }
    }
}
// 初始化

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
    ui.setOnCommandClick(handleCommand);
    ui.setOnWeightChange(handleWeight);
    ui.setOnChatSubmit(handlChatSubmit);

    // 4. 联网
    web.connectWiFi("CMCC-301", "15926081964");

    // 5. FreeRTOS 任务分配
    lvgl_mutex = xSemaphoreCreateMutex();
    chat_queue = xQueueCreate(5, sizeof(char[128]));

    // Core 1: 渲染 UI （高优先级）
    xTaskCreatePinnedToCore(
        TaskUI, "TaskUI", 8192, NULL, 5, NULL, 1
    );

    // Core 0: 处理后端网络请求 （低优先级）
    xTaskCreatePinnedToCore(
        TaskBackend, "TaskBackend", 8192, NULL, 2, NULL, 0
    );
}


void loop() {
    // 将 loop 交给 FreeRTOS 调度
    vTaskDelete(NULL);
}
