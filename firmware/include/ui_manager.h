#ifndef UI_MANAGER_H_
#define UI_MANAGER_H_

#include <lvgl.h>
#include <Arduino.h>


// 回调函数
typedef void (*CommandClickCallback)(const char* cmd);
typedef void (*WeightChangeCallback)(const char* weight);
typedef void (*ChatSubmitCallback)(const char* msg);


class UIManager {
public:
    UIManager();

    // 初始化 ui 页面
    void init();

    void updateStatus(const char* msg, bool isOnline);
    void addLog(const char* log);
    void updateStats(float cpu, float ram, const char* modelName);
    void addChatMessage(const char* role, const char* msg);

    // 回调函数
    void setOnCommandClick(CommandClickCallback cb);
    void setOnWeightChange(WeightChangeCallback cb);
    void setOnChatSubmit(ChatSubmitCallback cb);

private:
    lv_obj_t* _tabview;
    lv_obj_t* _status_label;
    lv_obj_t* _log_text;
    lv_obj_t* _cpu_bar;
    lv_obj_t* _model_label;
    lv_obj_t* _brightness_slider;
    lv_obj_t* _chat_list;
    lv_obj_t* _chat_input_ta;

    CommandClickCallback _onCommandClick = nullptr;
    WeightChangeCallback _onWeightChange = nullptr;
    ChatSubmitCallback _onChatSubmit = nullptr;


    // 构建页面函数
    void buildControlTab(lv_obj_t* parent);
    void buildStatsTab(lv_obj_t* parent);
    void buildConfigTab(lv_obj_t* parent);
    void buildChatTab(lv_obj_t* parent);

    // LVGL 事件中转
    static void btn_event_cb(lv_event_t* e);
    static void slider_event_cb(lv_event_t* e);
    static void dropdown_event_cb(lv_event_t* e);
    static void on_chat_send_event(lv_event_t* e);
    static void quick_reply_event_cb(lv_event_t* e);
};

#endif // UI_MANAGER_H_
