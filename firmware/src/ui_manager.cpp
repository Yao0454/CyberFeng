#include "ui_manager.h"

UIManager::UIManager() {}

void UIManager::init() {
    lv_obj_t* scr = lv_scr_act();
    lv_obj_set_style_bg_color(scr, lv_color_hex(0x000000), 0);

    //1. TabView
    _tabview = lv_tabview_create(scr, LV_DIR_TOP, 40);
    lv_obj_set_style_bg_color(_tabview, lv_color_hex(0x1A1A1A), LV_PART_MAIN);

    // Tab 按钮
    lv_obj_t* tab_btns = lv_tabview_get_tab_btns(_tabview);
    lv_obj_set_style_bg_color(tab_btns, lv_color_hex(0x333333), 0);
}