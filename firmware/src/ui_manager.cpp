#include <ui_manager.h>

UIManager::UIManager() {}

void UIManager::init() {
    _screen = lv_scr_act();
    lv_obj_set_style_bg_color(_screen, lv_palette_main(LV_PALETTE_GREY), 0);

    // 首先是标题
    lv_style_init(&_style_title);
    lv_style_set_text_font(&_style_title, &lv_font_montserrat_14);
    lv_style_set_text_color(&_style_title, lv_palette_main(LV_PALETTE_BLUE_GREY));

    

}