#include "ui_manager.h"

UIManager::UIManager() {}

void UIManager::init() {
    _screen = lv_scr_act();
    lv_obj_set_style_bg_color(_screen, lv_palette_main(LV_PALETTE_GREY), 0);

    // 1. 创建标题样式
    lv_style_init(&_style_title);
    lv_style_set_text_font(&_style_title, &lv_font_montserrat_14);
    lv_style_set_text_color(&_style_title, lv_palette_main(LV_PALETTE_BLUE_GREY));

    // 2. 标题标签
    lv_obj_t* title = lv_label_create(_screen);
    lv_obj_add_style(title, &_style_title, 0);
    lv_label_set_text(title, "CyberFeng Control");
    lv_obj_align(title, LV_ALIGN_TOP_MID, 0, 10);

    // 3. 状态显示框
    _status_label = lv_label_create(_screen);
    lv_label_set_text(_status_label, "Status: Offline");
    lv_obj_align(_status_label, LV_ALIGN_TOP_MID, 0, 45);

    // 4. 日志显示区域 (一个文本框)
    _log_text = lv_textarea_create(_screen);
    lv_obj_set_size(_log_text, 280, 100);
    lv_obj_align(_log_text, LV_ALIGN_CENTER, 0, 10);
    lv_textarea_set_placeholder_text(_log_text, "System logs...");
    lv_obj_set_style_text_font(_log_text, &lv_font_montserrat_14, 0);

    // 5. 操作按钮
    _action_btn = lv_btn_create(_screen);
    lv_obj_set_size(_action_btn, 120, 45);
    lv_obj_align(_action_btn, LV_ALIGN_BOTTOM_MID, 0, -10);
    
    lv_obj_t* btn_label = lv_label_create(_action_btn);
    lv_label_set_text(btn_label, "FETCH DATA");
    lv_obj_center(btn_label);

    // 重要：将当前对象的指针(this)存入按钮，方便回调函数访问
    lv_obj_add_event_cb(_action_btn, btn_event_handler, LV_EVENT_CLICKED, this);
}

// 静态回调逻辑
void UIManager::btn_event_handler(lv_event_t* e) {
    UIManager* instance = (UIManager*)lv_event_get_user_data(e);
    if (instance && instance->_external_cb) {
        instance->_external_cb(); // 调用 main.cpp 传入的逻辑
    }
}

void UIManager::setOnBtnClick(void (*callback)()) {
    _external_cb = callback;
}

void UIManager::updateServerStatus(const char* status, bool isOnline) {
    lv_label_set_text_fmt(_status_label, "Status: %s", status);
    lv_obj_set_style_text_color(_status_label, 
        isOnline ? lv_palette_main(LV_PALETTE_GREEN) : lv_palette_main(LV_PALETTE_RED), 0);
}

void UIManager::addLog(const char* log) {
    lv_textarea_add_text(_log_text, log);
    lv_textarea_add_text(_log_text, "\n");
}