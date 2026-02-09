#include <Arduino.h>
#include <TFT_eSPI.h>
#include <XPT2046_Touchscreen.h>
#include <lvgl.h>

// 硬件引脚
#define XPT2046_CS 33
#define XPT2046_CLK 25
#define XPT2046_MISO 39
#define XPT2046_MOSI 32

TFT_eSPI tft = TFT_eSPI();
SPIClass touchSpi = SPIClass(VSPI);
XPT2046_Touchscreen ts(XPT2046_CS);

// --- LVGL 显示刷新回调 ---
void my_disp_flush(lv_disp_drv_t *disp, const lv_area_t *area, lv_color_t *color_p) {
    uint32_t w = (area->x2 - area->x1 + 1);
    uint32_t h = (area->y2 - area->y1 + 1);
    tft.startWrite();
    tft.setAddrWindow(area->x1, area->y1, w, h);
    tft.pushColors((uint16_t *)&color_p->full, w * h, true);
    tft.endWrite();
    lv_disp_flush_ready(disp);
}

// --- LVGL 触摸读取回调 (使用你调好的校准值) ---
void my_touchpad_read(lv_indev_drv_t *indev_driver, lv_indev_data_t *data) {
    if (ts.touched()) {
        TS_Point p = ts.getPoint();
        // 过滤掉无效信号
        if (p.z > 4000 || p.z < 200 || p.x == 0 || p.y == 0) {
            data->state = LV_INDEV_STATE_REL;
            return;
        }
        // 映射坐标
        data->point.x = map(p.x, 200, 3800, 0, 320);
        data->point.y = map(p.y, 200, 3800, 0, 240);
        data->state = LV_INDEV_STATE_PR;
    } else {
        data->state = LV_INDEV_STATE_REL;
    }
}

// --- 按钮点击事件 ---
void btn_event_cb(lv_event_t * e) {
    lv_obj_t * btn = lv_event_get_target(e);
    static int cnt = 0;
    lv_obj_t * label = lv_obj_get_child(btn, 0);
    lv_label_set_text_fmt(label, "Clicked: %d", ++cnt);
}

void setup() {
    Serial.begin(115200);

    // 1. 硬件初始化
    tft.init();
    tft.setRotation(1);
    touchSpi.begin(XPT2046_CLK, XPT2046_MISO, XPT2046_MOSI, XPT2046_CS);
    ts.begin(touchSpi);
    ts.setRotation(1);

    // 2. LVGL 初始化
    lv_init();

    // 3. 设置 LVGL 显示缓冲区
    static lv_disp_draw_buf_t draw_buf;
    static lv_color_t buf[320 * 10]; // 10 行缓冲区
    lv_disp_draw_buf_init(&draw_buf, buf, NULL, 320 * 10);

    // 4. 设置显示驱动
    static lv_disp_drv_t disp_drv;
    lv_disp_drv_init(&disp_drv);
    disp_drv.hor_res = 320;
    disp_drv.ver_res = 240;
    disp_drv.flush_cb = my_disp_flush;
    disp_drv.draw_buf = &draw_buf;
    lv_disp_drv_register(&disp_drv);

    // 5. 设置输入驱动 (触摸)
    static lv_indev_drv_t indev_drv;
    lv_indev_drv_init(&indev_drv);
    indev_drv.type = LV_INDEV_TYPE_POINTER;
    indev_drv.read_cb = my_touchpad_read;
    lv_indev_drv_register(&indev_drv);

    // --- 6. 开启真正的 UI 之路 ---
    // 创建一个标题
    lv_obj_t * label = lv_label_create(lv_scr_act());
    lv_label_set_text(label, "Hello CYD World!");
    lv_obj_align(label, LV_ALIGN_TOP_MID, 0, 20);

    // 创建一个按钮
    lv_obj_t * btn = lv_btn_create(lv_scr_act());
    lv_obj_set_size(btn, 150, 50);
    lv_obj_align(btn, LV_ALIGN_CENTER, 0, -20);
    lv_obj_add_event_cb(btn, btn_event_cb, LV_EVENT_CLICKED, NULL);

    lv_obj_t * btn_label = lv_label_create(btn);
    lv_label_set_text(btn_label, "Click Me");
    lv_obj_center(btn_label);

    // 创建一个滑动条
    lv_obj_t * slider = lv_slider_create(lv_scr_act());
    lv_obj_set_width(slider, 200);
    lv_obj_align(slider, LV_ALIGN_BOTTOM_MID, 0, -40);
}

void loop() {
    lv_timer_handler(); // 处理 LVGL 任务
    delay(5);
}