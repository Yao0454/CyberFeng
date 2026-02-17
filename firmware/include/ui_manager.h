#ifndef UI_MANAGER_H
#define UI_MANAGER_H

#include <lvgl.h>
#include <Arduino.h>

class UIManager {
public:
    UIManager();

    // 初始化 ui 页面
    void init();

    void updateStatus(const char* msg, bool isOnline);
    void addLog(const char* log);
    void updateStats(float cpu, float ram, const char* modelName);

    // 回调函数
    void setOnCommandClick(void (*cb)(const char* cmd));
    void setOnWeightChange(void (*cb)(const char* weightName));
 
private:
    lv_obj_t* _tabview;
    lv_obj_t* _status_label;
    lv_obj_t* _log_text;
    lv_obj_t* _cpu_bar;
    lv_obj_t* _model_label;
    lv_obj_t* _brightness_slider;

    void (*_cmd_cb)(const char*) = nullptr;
    void (*_weight_cb)(const char*) = nullptr;


    // 构建页面函数
    void buildControlTab(lv_obj_t* parent);
    void buildStatsTab(lv_obj_t* parent);
    void buildConfigTab(lv_obj_t* parent);

    // LVGL 事件中转
    static void btn_event_cb(lv_event_t* e);
    static void slider_event_cb(lv_event_t* e);
    static void dropdown_event_cb(lv_event_t* e);
};


#endif