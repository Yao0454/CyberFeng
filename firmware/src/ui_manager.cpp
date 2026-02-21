#include "ui_manager.h"
#include "core/lv_event.h"
#include "core/lv_obj.h"
#include "core/lv_obj_pos.h"
#include "extra/widgets/list/lv_list.h"
#include "misc/lv_area.h"
#include "misc/lv_color.h"
#include "widgets/lv_btn.h"
#include "widgets/lv_label.h"
#include "widgets/lv_textarea.h"
#include <cstring>

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

    // 2. Four Pages
    lv_obj_t* t1 = lv_tabview_add_tab(_tabview, "Control");
    lv_obj_t* t2 = lv_tabview_add_tab(_tabview, "Stats");
    lv_obj_t* t3 = lv_tabview_add_tab(_tabview, "Config");
    lv_obj_t* t4 = lv_tabview_add_tab(_tabview, "Chat");

    buildControlTab(t1);
    buildStatsTab(t2);
    buildConfigTab(t3);
    buildChatTab(t4);
}

void UIManager::buildChatTab(lv_obj_t* parent) {

    // 聊天列表 (上半部分)
    _chat_list = lv_list_create(parent);
    lv_obj_set_size(_chat_list, 300, 110);
    lv_obj_align(_chat_list, LV_ALIGN_TOP_MID, 0, 0);

    // 输入框 （左下角）
    _chat_input_ta = lv_textarea_create(parent);
    lv_obj_set_size(_chat_input_ta, 220, 40);
    lv_obj_align(_chat_input_ta, LV_ALIGN_BOTTOM_LEFT, 10, -5);
    lv_textarea_set_one_line(_chat_input_ta, true);
    lv_textarea_set_placeholder_text(_chat_input_ta, "Type message...");

    // 发送按钮（右下角）
    lv_obj_t* send_btn = lv_btn_create(parent);
    lv_obj_set_size(send_btn, 60, 40);
    lv_obj_align(send_btn, LV_ALIGN_BOTTOM_RIGHT, -10, -5);
    lv_obj_set_style_bg_color(send_btn, lv_palette_main(LV_PALETTE_BLUE), 0);

    lv_obj_t* send_lbl = lv_label_create(send_btn);
    lv_label_set_text(send_lbl, "Send");
    lv_obj_center(send_lbl);

    // 绑定发送事件
    lv_obj_add_event_cb(send_btn, on_chat_send_event, LV_EVENT_CLICKED, this);
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

void UIManager::addChatMessage(const char* role, const char* msg) {
    if (_chat_list) return;

    String fullMsg = String(role) + ": " + String(msg);
    lv_obj_t* btn = lv_list_add_btn(_chat_list, LV_SYMBOL_DUMMY, fullMsg.c_str());

    lv_obj_t* label = lv_obj_get_child(btn, 0);
    if (label) {
        lv_label_set_long_mode(label, LV_LABEL_LONG_WRAP);
        lv_obj_set_width(label, 260);

    }

    lv_obj_scroll_to_view(btn, LV_ANIM_ON);
}

void UIManager::buildConfigTab(lv_obj_t* parent) {
    lv_obj_t* l1 = lv_label_create(parent);
    lv_label_set_text(l1, "Model Weight:");
    lv_obj_align(l1, LV_ALIGN_TOP_LEFT, 20, 10);

    // 下拉选择框
    lv_obj_t* dd = lv_dropdown_create(parent);
    lv_dropdown_set_options(dd, "GPT_weights_v4/CyberFeng-e25.ckpt");
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

    if (inst->_onCommandClick) inst->_onCommandClick(txt);
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
    if (inst->_onWeightChange) inst->_onWeightChange(buf);
}

void UIManager::on_chat_send_event(lv_event_t* e) {
    UIManager* inst = (UIManager*)lv_event_get_user_data(e);
    if (!inst->_chat_input_ta) return;

    const char* txt = lv_textarea_get_text(inst->_chat_input_ta);
    if (strlen(txt) > 0) {
        if (inst->_onChatSubmit) inst->_onChatSubmit(txt);

        inst->addChatMessage("Me", txt);

        lv_textarea_set_text(inst->_chat_input_ta, "");
    }
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

void UIManager::setOnCommandClick(void (*cb)(const char*)) { _onCommandClick = cb; }
void UIManager::setOnWeightChange(void (*cb)(const char*)) { _onWeightChange = cb; }
void UIManager::setOnChatSubmit(void (*cb)(const char*)) { _onChatSubmit = cb; }
