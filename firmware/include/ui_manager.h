#ifndef UI_MANAGER_H
#define UI_MANAGER_H

#include <lvgl.h>
#include <Arduino.h>

class UIManager {
public:
    UIManager();

    // 初始化 ui 页面
    void init();

    // 更新服务器状态文字接口
    void updateServerStatus(const char* status, bool isOnline);

    // 更新日志或数据的接口
    void addLog(const char* log);

    // 设置按钮点击的回调函数
    void setOnBtnClick(void (*callback)());

private:
    // 内部组件指针
    lv_obj_t* _screen;
    lv_obj_t* _status_label;
    lv_obj_t* _log_text;
    lv_obj_t* _action_btn;

    // 样式对象
    lv_style_t _style_btn;
    lv_style_t _style_title;

    // 静态回调函数
    static void btn_event_handler(lv_event_t* e);

    // 保存外部传入的回调
    void (*_external_cb)() = nullptr;

};


#endif