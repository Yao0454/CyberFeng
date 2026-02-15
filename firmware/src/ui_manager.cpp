#include <ui_manager.h>

UIManager::UIManager() {}

void UIManager::init() {
    _screen = lv_scr_act();
    lv_obj_set_style_bg_color(_screen, lv_palette_main(LV_PALETTE_GREY), 0);

    // 首先是标题
    lv_style_init(&_style_title);
    lv_style_set_text_font(&_style_title, &lv_font_montserrat_14);
    lv_style_set_text_color(&_style_title, lv_palette_main(LV_PALETTE_BLUE_GREY));

    // 标题标签
    lv_obj_t* title = lv_label_create(_screen);
    lv_obj_add_style(title, &_style_title, 0);
    lv_label_set_text(title, "CyberFeng Control");
    lv_obj_align(title, LV_ALIGN_TOP_MID, 0, 10);

    // 状态栏
    _status_label = lv_label_create(_screen);
    lv_label_set_text(_status_label, "Status: Offline");
    lv_obj_align(_status_label, LV_ALIGN_TOP_MID, 0, 45);
}