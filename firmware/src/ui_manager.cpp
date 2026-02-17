#include "ui_manager.h"

UIManager::UIManager() {}

void UIManager::init() {
    _screen = lv_scr_act();

    // 选项卡页面 
    lv_obj_t* tabview = lv_tabview_create(_screen, LV_DIR_TOP, 40);

    // 然后添加三个子页面
    lv_obj_t* t1 = lv_tabview_add_tab(tabview, "Control");
    lv_obj_t* t2 = lv_tabview_add_tab(tabview, "Status");
    lv_obj_t* t3 = lv_tabview_add_tab(tabview, "Settings");
    

    // 1. Control
    _action_btn = lv_btn_create(t1);
    lv_obj_set_size(_action_btn, 120, 50);
    lv_obj_align(_action_btn, LV_ALIGN_CENTER, 0, 0);
    lv_obj_t* btn_lbl = lv_label_create(_action_btn);
    lv_label_set_text(btn_lbl, "RESTART CF");
    lv_obj_add_event_cb(_action_btn, btn_event_handler, LV_EVENT_CLICKED, this);

    // 2. Status
    _status_label = lv_label_create(t2);
    lv_label_set_text(_status_label, "Server Status:");
    lv_obj_align(_status_label, LV_ALIGN_TOP_LEFT, 10, 10);
    lv_obj_t* bar = lv_bar_create(t2);
    lv_obj_set_size(bar, 200, 20);
    lv_obj_center(bar);
    lv_bar_set_value(bar, 70, LV_ANIM_ON);

    // 3. Log
    _log_text = lv_textarea_create(t3);
    lv_obj_set_size(_log_text, 280, 150);
    lv_obj_center(_log_text);

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