# -*- coding: utf-8 -*-
"""统一 UI 视觉样式。

把「右键菜单 / 托盘菜单 / 设置窗口」的 QSS 集中在这里，
跟随当前主题的强调色与明暗，做到三处风格一致。

只负责外观，不含任何业务逻辑；主题切换时重新取样式表即可，
不会影响计时器（单调时钟 deadline 保持不变）。
"""
from theme import get_palette

_FONT = ('"Microsoft YaHei UI", "Microsoft YaHei", "PingFang SC", '
         '"Segoe UI", sans-serif')


def _hex(c):
    """(r,g,b[,a]) -> #rrggbb"""
    return '#%02x%02x%02x' % (c[0], c[1], c[2])


def _rgba(c, a):
    return 'rgba(%d, %d, %d, %.2f)' % (c[0], c[1], c[2], a)


def accent(theme_key):
    """当前主题的强调色（取工作态进度环主色）。"""
    return _hex(get_palette(theme_key)['ring_work1'])


def menu_stylesheet(theme_key='deep_space'):
    """右键菜单 / 托盘菜单共用的精致菜单样式。"""
    p = get_palette(theme_key)
    bg, text = p['menu_bg'], p['menu_text']
    sel, border, sep = p['menu_sel'], p['menu_border'], p['menu_sep']
    acc = _hex(p['ring_work1'])
    # 选中态在主题色基础上叠一层强调色渐变，更有层次
    return f"""
    QMenu {{
        background-color: {bg};
        color: {text};
        border: 1px solid {border};
        border-radius: 10px;
        padding: 3px 4px;
        font-family: {_FONT};
    }}
    QMenu::item {{
        padding: 4px 24px 4px 30px;
        margin: 0 1px;
        border-radius: 5px;
        font-size: 11px;
    }}
    QMenu::item:selected {{
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {sel}, stop:1 {acc}38);
        color: {text};
    }}
    QMenu::item:disabled {{ color: {sep}; }}
    QMenu::separator {{
        height: 1px;
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 transparent, stop:0.5 {sep}, stop:1 transparent);
        margin: 2px 10px;
    }}
    QMenu::indicator {{
        width: 13px; height: 13px;
        left: 9px;
        border: 1px solid {border};
        border-radius: 4px;
        background-color: transparent;
    }}
    QMenu::indicator:checked {{
        background-color: {acc};
        border-color: {acc};
    }}
    """


def settings_stylesheet(theme_key='deep_space'):
    """设置窗口样式：跟随主题明暗的卡片式设计。"""
    p = get_palette(theme_key)
    dark = p['is_dark']
    acc = _hex(p['ring_work1'])

    if dark:
        bg, card, card_border = '#1c1c26', '#262632', '#333342'
        text, sub, input_bg, input_border = '#ececf3', '#8f8fa2', '#1f1f2a', '#3a3a4a'
        field_sel = _rgba(p['ring_work1'], 0.38)
        primary_text = '#ffffff'
        btn_sec_bg, btn_sec_border = '#2c2c3a', '#3a3a4a'
    else:
        bg, card, card_border = '#eef0f5', '#ffffff', '#e2e5ee'
        text, sub, input_bg, input_border = '#2a2c3a', '#83879a', '#f6f7fb', '#d8dbe6'
        field_sel = _rgba(p['ring_work1'], 0.22)
        primary_text = '#ffffff'
        btn_sec_bg, btn_sec_border = '#ffffff', '#d8dbe6'

    acc2 = _hex(p['ring_work2'])

    return f"""
    QDialog#SettingsDialog {{
        background-color: {bg};
        font-family: {_FONT};
    }}
    QWidget {{ font-family: {_FONT}; }}

    /* 顶部品牌区：强调色渐变横幅 */
    QFrame#Header {{
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 {acc}, stop:1 {acc2});
        border-radius: 12px;
    }}
    QLabel#HeaderTitle {{
        color: #ffffff;
        font-size: 15px;
        font-weight: bold;
        background: transparent;
    }}
    QLabel#HeaderSub {{
        color: rgba(255, 255, 255, 200);
        font-size: 9px;
        background: transparent;
    }}
    QLabel#HeaderIcon {{ background: transparent; }}

    /* 分组：无卡片底，仅用细分隔线区分 */
    QGroupBox {{
        background: transparent;
        border: none;
        border-bottom: 1px solid {input_border};
        border-radius: 0;
        margin: 6px 0 0 0;
        padding: 13px 0 9px 0;
        font-size: 13px;
        font-weight: 600;
        color: {acc};
    }}
    QGroupBox::title {{
        subcontrol-origin: padding;
        subcontrol-position: top left;
        left: 0;
        top: 2px;
        padding: 0 6px 0 0;
    }}
    QLabel {{
        color: {text};
        font-size: 12px;
        background: transparent;
    }}

    /* 输入框 */
    QSpinBox, QComboBox {{
        background-color: {input_bg};
        border: 1px solid {input_border};
        border-radius: 7px;
        padding: 4px 9px;
        min-height: 22px;
        color: {text};
        font-size: 11px;
        selection-background-color: {acc};
    }}
    QSpinBox:hover, QComboBox:hover {{ border-color: {acc}; }}
    QSpinBox:focus, QComboBox:focus {{ border: 1px solid {acc}; }}
    QComboBox::drop-down {{ border: none; width: 20px; }}
    QComboBox::down-arrow {{
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 5px solid {sub};
        margin-right: 7px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {card};
        color: {text};
        selection-background-color: {field_sel};
        border: 1px solid {card_border};
        border-radius: 8px;
        outline: none;
        padding: 4px;
    }}

    /* 复选框 */
    QCheckBox {{
        color: {text};
        font-size: 11px;
        spacing: 7px;
        background: transparent;
    }}
    QCheckBox::indicator {{
        width: 17px; height: 17px;
        border: 1px solid {input_border};
        border-radius: 5px;
        background-color: {input_bg};
    }}
    QCheckBox::indicator:hover {{ border-color: {acc}; }}
    QCheckBox::indicator:checked {{
        background-color: {acc};
        border-color: {acc};
    }}

    /* 按钮 */
    QPushButton {{
        font-family: {_FONT};
        font-size: 11px;
        padding: 5px 14px;
        min-width: 64px;
        min-height: 24px;
        border-radius: 8px;
    }}
    QPushButton#PrimaryButton {{
        background-color: {acc};
        color: {primary_text};
        border: 1px solid {acc};
        font-weight: bold;
    }}
    QPushButton#PrimaryButton:hover {{
        background-color: {field_sel};
        border-color: {acc};
    }}
    QPushButton#SecondaryButton {{
        background-color: {btn_sec_bg};
        color: {text};
        border: 1px solid {btn_sec_border};
    }}
    QPushButton#SecondaryButton:hover {{ border-color: {acc}; }}
    QPushButton:pressed {{ margin-top: 1px; }}

    /* 扁平主题色卡 */
    QFrame#ThemeCard {{
        background: transparent;
        border: 1px solid {input_border};
        border-radius: 8px;
    }}
    QFrame#ThemeCard:hover {{ border-color: {acc}; }}
    QFrame#ThemeCard[selected="true"] {{
        border: 1px solid {acc};
        background-color: {field_sel};
    }}
    QLabel#ThemeCardName {{
        font-size: 10px;
        color: {text};
    }}
    QFrame#ThemeCard[selected="true"] QLabel#ThemeCardName {{
        color: {acc};
        font-weight: bold;
    }}
    """
