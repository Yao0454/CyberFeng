#include "ui_manager.h"

UIManager::UIManager() {}

void UIManager::init() {
    lv_obj_t* scr = lv_scr_act();
    lv_obj_set_style_bg_color(scr, lv_color_hex(0x000000), 0);

    // 1. TabView
    _tabview = lv_tabview_create(scr, LV_DIR_TOP, 40);
    lv_obj_set_style_bg_color(_tabview, lv_color_hex(0x1A1A1A), LV_PART_MAIN);

    // Tab 按钮
    lv_obj_t* tab_btns = lv_tabview_get_tab_btns(_tabview);
    lv_obj_set_style_bg_color(tab_btns, lv_color_hex(0x333333), 0);
    lv_obj_set_style_text_color(tab_btns, lv_color_hex(0x00FFFF), 0);

    // 2. Three Pages
    lv_obj_t* t1 = lv_tabview_add_tab(_tabview, "Control");
    lv_obj_t* t2 = lv_tabview_add_tab(_tabview, "Stats");
    lv_obj_t* t3 = lv_tabview_add_tab(_tabview, "Config");

    buildControlTab(t1);
    buildStatsTab(t2);
    buildConfigTab(t3);

}

void UIManager::buildControlTab(lv_obj_t* parent) {
    // 状态栏
    _status_label = lv_label_create(parent);
    lv_label_set_text(_status_label, "System: Ready");
    lv_obj_align(_status_label, LV_ALIGN_TOP_MID, 0, 0);

    // 重启 TTS 按钮
    lv_obj_t* btn = lv_btn_create(parent);
    lv_obj_set_size(btn, 100, 40);
    lv_obj_align(btn, LV_ALIGN_TOP_LEFT, 10, 30);
    lv_obj_set_style_bg_color(btn, lv_palette_main(LV_PALETTE_RED), 0);
    lv_obj_t* lbl = lv_label_create(btn);
    lv_label_set_text(lbl, "RESTART");
    lv_obj_center(lbl);
    lv_obj_add_event_cb(btn, btn_event_cb, LV_EVENT_CLICKED, this);

    // Log 栏
    _log_text = lv_textarea_create(parent);
    lv_obj_set_size(_log_text, 300, 90);
    lv_obj_align(_log_text, LV_ALIGN_BOTTOM_MID, 0, -5);
    lv_obj_set_style_bg_color(_log_text, lv_color_hex(0x00FF00), 0);
    lv_textarea_set_cursor_click_pos(_log_text, false);
}

void UIManager::buildStatsTab(lv_obj_t* parent) {
    lv_obj_t* l1 = lv_label_create(parent);
    lv_label_set_text(l1, "BACKED CPU:");
    lv_obj_align(l1, LV_ALIGN_TOP_LEFT, 20, 20);

    _cpu_bar = lv_bar_create(parent);
    lv_obj_set_size(_cpu_bar, 200, 20);
    lv_obj_align(_cpu_bar, LV_ALIGN_TOP_LEFT, 20, 45);
    lv_bar_set_value(_cpu_bar, 0, LV_ANIM_ON);

    _model_label = lv_label_create(parent);
    lv_obj_align(_model_label, LV_ALIGN_TOP_LEFT, 20, 80);
    lv_label_set_text_fmt(_model_label, "Active Model %s", "None");
}

void UIManager::buildConfigTab(lv_obj_t* parent) {
    lv_obj_t* l1 = lv_label_create(parent);
    lv_label_set_text(l1, "Model Weight:");
    lv_obj_align(l1, LV_ALIGN_TOP_LEFT, 20, 10);

    // 下拉选择框
    lv_obj_t* dd = lv_dropdown_create(parent);
    lv_dropdown_set_options(dd, "CyberFeng_V1\nGirl_Voice\nAnime_V3\nHeavy_Bass");
    lv_obj_align(dd, LV_ALIGN_TOP_LEFT, 20, 35);
    lv_obj_add_event_cb(dd, dropdown_event_cb, LV_EVENT_VALUE_CHANGED, this);

    // 屏幕亮度调节
    lv_obj_t* l2 = lv_label_create(parent);
    lv_label_set_text(l2, "LCD Brightness:");
    lv_obj_align(l2, LV_ALIGN_TOP_LEFT, 20, 90);

    _brightness_slider = lv_slider_create(parent);
    lv_obj_set_size(_brightness_slider, 200, 10);
    lv_obj_align(_brightness_slider, LV_ALIGN_TOP_LEFT, 20, 115);
    lv_slider_set_range(_brightness_slider, 10, 255);
    lv_slider_set_value(_brightness_slider, 255, LV_ANIM_OFF);
    lv_obj_add_event_cb(_brightness_slider, slider_event_cb, LV_EVENT_VALUE_CHANGED, this);
}

// 事件中转实现
void UIManager::btn_event_cb(lv_event_t* e) {
    UIManager* inst = (UIManager*)lv_event_get_user_data(e);
    lv_obj_t* target = lv_event_get_target(e);
    lv_obj_t* label = lv_obj_get_child(target, 0);
    const char* txt = lv_label_get_text(label);
    
    if (inst->_cmd_cb) inst->_cmd_cb(txt);
}

void UIManager::slider_event_cb(lv_event_t* e) {
    lv_obj_t* slider = lv_event_get_target(e);
    int val = lv_slider_get_value(slider);
    analogWrite(21, val); // 直接调节背光引脚
}

void UIManager::dropdown_event_cb(lv_event_t* e) {
    UIManager* inst = (UIManager*)lv_event_get_user_data(e);
    lv_obj_t* dd = lv_event_get_target(e);
    char buf[64];
    lv_dropdown_get_selected_str(dd, buf, sizeof(buf));
    if (inst->_weight_cb) inst->_weight_cb(buf);
}

// 接口实现
void UIManager::updateStatus(const char* msg, bool isOnline) {
    lv_label_set_text(_status_label, msg);
    lv_obj_set_style_text_color(_status_label, isOnline ? lv_color_hex(0x00FF00) : lv_color_hex(0xFF0000), 0);
}

void UIManager::addLog(const char* log) {
    lv_textarea_add_text(_log_text, log);
    lv_textarea_add_text(_log_text, "\n");
}

void UIManager::updateStats(float cpu, float ram, const char* model) {
    lv_bar_set_value(_cpu_bar, (int)cpu, LV_ANIM_ON);
    lv_label_set_text_fmt(_model_label, "Active Model: %s", model);
}

void UIManager::setOnCommandClick(void (*cb)(const char*)) { _cmd_cb = cb; }
void UIManager::setOnWeightChange(void (*cb)(const char*)) { _weight_cb = cb; }
