"""全局唯一的番茄图标来源。

所有窗口（主窗口、设置、历史）、系统托盘、EXE 都从这里取图标，
保证整个软件视觉统一。兼容开发环境与 PyInstaller 打包后的 EXE。
"""
import os
import sys

from PySide6.QtGui import QIcon

_ICON_FILE = os.path.join('assets', 'app.ico')


def icon_path():
    """返回番茄图标的绝对路径（文件不存在时也返回路径，便于调试）。"""
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, _ICON_FILE)


def get_app_icon():
    """返回全局番茄图标 QIcon；若文件缺失则返回空图标，不影响运行。"""
    path = icon_path()
    if os.path.exists(path):
        return QIcon(path)
    return QIcon()
