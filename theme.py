"""主题配色定义。

每套主题是一组字典，供窗口绘制 / 样式表 / 进度环使用。
颜色统一用 (r, g, b, a) 元组，方便 QColor 构造和字符串拼接。
"""

# 主题显示名 -> key（保留旧接口；界面显示统一走 theme_label，支持多语言）
THEMES = {
    "经典深空": "deep_space",
    "清爽浅色": "light",
    "番茄红": "tomato",
    "森林绿": "forest",
    "iOS 现代风": "ios",
}

# 主题 key -> 英文原文（作为翻译 key）
THEME_LABELS = {
    "deep_space": "Classic Deep Space",
    "light": "Light",
    "tomato": "Tomato Red",
    "forest": "Forest Green",
    "ios": "iOS Modern",
}

# 每套主题的完整配色
PALETTES = {
    "deep_space": {
        "name": "经典深空",
        "is_dark": True,
        # 窗口背景渐变：工作态 / 休息态
        "bg_top": (26, 26, 36, 175),
        "bg_bottom": (20, 20, 30, 185),
        "bg_top_break": (20, 36, 28, 175),
        "bg_bottom_break": (16, 30, 24, 185),
        "highlight": (255, 255, 255, 18),
        "highlight_end": (255, 255, 255, 0),
        "border": (255, 255, 255, 12),
        # 文字
        "time_color": (255, 255, 255, 245),
        # 按钮（用 rgba 字符串）
        "btn_color": "rgba(255, 255, 255, 0.82)",
        "btn_hover_color": "rgba(255, 255, 255, 1.0)",
        "btn_hover_bg": "rgba(255, 255, 255, 0.08)",
        "btn_pressed_bg": "rgba(255, 255, 255, 0.16)",
        # 下拉框
        "combo_bg": "rgba(255, 255, 255, 0.06)",
        "combo_color": "rgba(255, 255, 255, 0.88)",
        "combo_arrow": "rgba(255, 255, 255, 0.6)",
        "popup_bg": "#1a1a28",
        "popup_text": "#e0e0e8",
        "popup_sel": "#2e2e44",
        "popup_border": "#2a2a3c",
        # 菜单
        "menu_bg": "#1a1a28",
        "menu_text": "#e0e0e8",
        "menu_sel": "#2e2e44",
        "menu_border": "#2e2e44",
        "menu_sep": "#2e2e44",
        # 进度环
        "ring_bg": (255, 255, 255, 35),
        "ring_work1": (255, 95, 75),
        "ring_work2": (255, 160, 110),
        "ring_break1": (70, 210, 150),
        "ring_break2": (120, 230, 180),
        "ring_inner_work1": (255, 95, 75, 22),
        "ring_inner_work2": (255, 160, 110, 35),
        "ring_inner_break1": (70, 210, 150, 22),
        "ring_inner_break2": (120, 230, 180, 35),
    },
    "light": {
        "name": "清爽浅色",
        "is_dark": False,
        "bg_top": (250, 250, 253, 232),
        "bg_bottom": (235, 235, 242, 240),
        "bg_top_break": (240, 250, 244, 232),
        "bg_bottom_break": (225, 242, 232, 240),
        "highlight": (255, 255, 255, 150),
        "highlight_end": (255, 255, 255, 0),
        "border": (255, 255, 255, 180),
        "time_color": (40, 42, 54, 255),
        "btn_color": "rgba(50, 52, 66, 0.85)",
        "btn_hover_color": "rgba(20, 22, 34, 1.0)",
        "btn_hover_bg": "rgba(0, 0, 0, 0.06)",
        "btn_pressed_bg": "rgba(0, 0, 0, 0.12)",
        "combo_bg": "rgba(0, 0, 0, 0.04)",
        "combo_color": "rgba(40, 42, 54, 0.9)",
        "combo_arrow": "rgba(40, 42, 54, 0.55)",
        "popup_bg": "#ffffff",
        "popup_text": "#2a2c3a",
        "popup_sel": "#e6e8f0",
        "popup_border": "#d4d6e0",
        "menu_bg": "#ffffff",
        "menu_text": "#2a2c3a",
        "menu_sel": "#e6e8f0",
        "menu_border": "#d4d6e0",
        "menu_sep": "#e0e2ea",
        "ring_bg": (0, 0, 0, 28),
        "ring_work1": (230, 80, 70),
        "ring_work2": (245, 140, 100),
        "ring_break1": (46, 180, 120),
        "ring_break2": (90, 210, 150),
        "ring_inner_work1": (230, 80, 70, 18),
        "ring_inner_work2": (245, 140, 100, 28),
        "ring_inner_break1": (46, 180, 120, 18),
        "ring_inner_break2": (90, 210, 150, 28),
    },
    "tomato": {
        "name": "番茄红",
        "is_dark": True,
        "bg_top": (92, 26, 28, 200),
        "bg_bottom": (64, 18, 22, 215),
        "bg_top_break": (40, 52, 34, 200),
        "bg_bottom_break": (28, 40, 26, 215),
        "highlight": (255, 220, 220, 22),
        "highlight_end": (255, 220, 220, 0),
        "border": (255, 190, 190, 22),
        "time_color": (255, 245, 240, 255),
        "btn_color": "rgba(255, 235, 230, 0.9)",
        "btn_hover_color": "rgba(255, 255, 255, 1.0)",
        "btn_hover_bg": "rgba(255, 200, 190, 0.12)",
        "btn_pressed_bg": "rgba(255, 200, 190, 0.22)",
        "combo_bg": "rgba(255, 220, 210, 0.10)",
        "combo_color": "rgba(255, 240, 235, 0.92)",
        "combo_arrow": "rgba(255, 220, 210, 0.65)",
        "popup_bg": "#3a1216",
        "popup_text": "#ffede8",
        "popup_sel": "#5a1e22",
        "popup_border": "#6a2a2e",
        "menu_bg": "#3a1216",
        "menu_text": "#ffede8",
        "menu_sel": "#5a1e22",
        "menu_border": "#6a2a2e",
        "menu_sep": "#5a2226",
        "ring_bg": (255, 210, 200, 40),
        "ring_work1": (255, 130, 100),
        "ring_work2": (255, 200, 130),
        "ring_break1": (150, 220, 130),
        "ring_break2": (200, 240, 150),
        "ring_inner_work1": (255, 130, 100, 26),
        "ring_inner_work2": (255, 200, 130, 40),
        "ring_inner_break1": (150, 220, 130, 26),
        "ring_inner_break2": (200, 240, 150, 40),
    },
    "forest": {
        "name": "森林绿",
        "is_dark": True,
        "bg_top": (18, 48, 38, 200),
        "bg_bottom": (12, 36, 28, 215),
        "bg_top_break": (26, 58, 44, 200),
        "bg_bottom_break": (18, 46, 34, 215),
        "highlight": (220, 255, 235, 20),
        "highlight_end": (220, 255, 235, 0),
        "border": (200, 255, 225, 20),
        "time_color": (235, 255, 242, 255),
        "btn_color": "rgba(225, 255, 238, 0.85)",
        "btn_hover_color": "rgba(255, 255, 255, 1.0)",
        "btn_hover_bg": "rgba(120, 220, 170, 0.12)",
        "btn_pressed_bg": "rgba(120, 220, 170, 0.22)",
        "combo_bg": "rgba(150, 230, 190, 0.10)",
        "combo_color": "rgba(230, 255, 240, 0.9)",
        "combo_arrow": "rgba(180, 240, 205, 0.65)",
        "popup_bg": "#102c22",
        "popup_text": "#e0ffee",
        "popup_sel": "#1c4636",
        "popup_border": "#2a5a46",
        "menu_bg": "#102c22",
        "menu_text": "#e0ffee",
        "menu_sel": "#1c4636",
        "menu_border": "#2a5a46",
        "menu_sep": "#1c4032",
        "ring_bg": (200, 255, 225, 40),
        "ring_work1": (255, 170, 110),
        "ring_work2": (255, 210, 140),
        "ring_break1": (90, 220, 160),
        "ring_break2": (150, 240, 190),
        "ring_inner_work1": (255, 170, 110, 24),
        "ring_inner_work2": (255, 210, 140, 38),
        "ring_inner_break1": (90, 220, 160, 24),
        "ring_inner_break2": (150, 240, 190, 38),
    },
    "ios": {
        "name": "iOS 现代风",
        "is_dark": True,
        "bg_top": (44, 44, 48, 195),
        "bg_bottom": (30, 30, 34, 210),
        "bg_top_break": (38, 46, 54, 195),
        "bg_bottom_break": (26, 32, 40, 210),
        "highlight": (255, 255, 255, 26),
        "highlight_end": (255, 255, 255, 0),
        "border": (255, 255, 255, 20),
        "time_color": (255, 255, 255, 255),
        "btn_color": "rgba(255, 255, 255, 0.9)",
        "btn_hover_color": "rgba(255, 255, 255, 1.0)",
        "btn_hover_bg": "rgba(255, 255, 255, 0.10)",
        "btn_pressed_bg": "rgba(255, 255, 255, 0.20)",
        "combo_bg": "rgba(255, 255, 255, 0.08)",
        "combo_color": "rgba(255, 255, 255, 0.92)",
        "combo_arrow": "rgba(255, 255, 255, 0.65)",
        "popup_bg": "#2c2c2e",
        "popup_text": "#f2f2f7",
        "popup_sel": "#3a3a3c",
        "popup_border": "#48484a",
        "menu_bg": "#2c2c2e",
        "menu_text": "#f2f2f7",
        "menu_sel": "#3a3a3c",
        "menu_border": "#48484a",
        "menu_sep": "#3a3a3c",
        "ring_bg": (255, 255, 255, 30),
        "ring_work1": (255, 159, 10),
        "ring_work2": (255, 214, 90),
        "ring_break1": (48, 209, 88),
        "ring_break2": (100, 235, 150),
        "ring_inner_work1": (255, 159, 10, 22),
        "ring_inner_work2": (255, 214, 90, 36),
        "ring_inner_break1": (48, 209, 88, 22),
        "ring_inner_break2": (100, 235, 150, 36),
    },
}



# 长休息独立配色（紫色系），不改动原有 5 套主题的其他键值
_LONG_BREAK_COLORS = {
    "deep_space": dict(ring_long1=(155, 140, 255), ring_long2=(195, 182, 255),
                       ring_inner_long1=(155, 140, 255, 22),
                       ring_inner_long2=(195, 182, 255, 35),
                       bg_top_long=(28, 26, 48, 175), bg_bottom_long=(22, 20, 36, 185)),
    "light": dict(ring_long1=(116, 103, 232), ring_long2=(165, 154, 255),
                  ring_inner_long1=(116, 103, 232, 18),
                  ring_inner_long2=(165, 154, 255, 28),
                  bg_top_long=(242, 240, 252, 232), bg_bottom_long=(228, 224, 245, 240)),
    "tomato": dict(ring_long1=(255, 176, 160), ring_long2=(255, 217, 192),
                   ring_inner_long1=(255, 176, 160, 26),
                   ring_inner_long2=(255, 217, 192, 40),
                   bg_top_long=(58, 28, 36, 200), bg_bottom_long=(38, 20, 28, 215)),
    "forest": dict(ring_long1=(127, 212, 200), ring_long2=(182, 236, 226),
                   ring_inner_long1=(127, 212, 200, 24),
                   ring_inner_long2=(182, 236, 226, 38),
                   bg_top_long=(20, 46, 42, 200), bg_bottom_long=(14, 34, 32, 215)),
    "ios": dict(ring_long1=(94, 159, 255), ring_long2=(154, 197, 255),
                ring_inner_long1=(94, 159, 255, 22),
                ring_inner_long2=(154, 197, 255, 36),
                bg_top_long=(34, 40, 52, 195), bg_bottom_long=(24, 28, 40, 210)),
}
for _key, _extra in _LONG_BREAK_COLORS.items():
    if _key in PALETTES:
        PALETTES[_key].update(_extra)


def get_palette(key):
    """取主题配色；未知 key 回退到经典深空。"""
    return PALETTES.get(key, PALETTES["deep_space"])


def theme_names():
    """返回主题显示名列表（兼容旧调用，固定为中文名）。"""
    return list(THEMES.keys())


def theme_keys():
    """返回主题 key 列表（保持定义顺序）。"""
    return [key for key in THEMES.values()]


def theme_label(key):
    """返回当前界面语言的主题显示名。"""
    from i18n import tr
    return tr(THEME_LABELS.get(key, 'Classic Deep Space'))
