# -*- coding: utf-8 -*-
"""离屏启动真实软件，抓取窗口/菜单/设置对话框的高清截图素材。

产物保存到 docs/images/_capture/，供 draw_preview.py 排版使用。
"""
import os
import sys
import tempfile

# 高 DPI 缩放，抓到更清晰的素材
os.environ.setdefault("QT_SCALE_FACTOR", "3")
os.environ["QT_QPA_PLATFORM"] = "windows"
os.environ["QT_QPA_FONTDIR"] = "C:/Windows/Fonts"
os.environ["APPDATA"] = tempfile.mkdtemp(prefix="pomodoro-capture-")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont, QFontDatabase

app = QApplication([])
app.setFont(QFont("Microsoft YaHei", 10))

from main import PomodoroApp
from settings import SettingsDialog
from history_dialog import HistoryDialog
from appbar_window import _TopmostMenu

OUT = os.path.join(ROOT, "docs", "images", "_capture")
os.makedirs(OUT, exist_ok=True)

p = PomodoroApp()
p.create_window()
p.create_tray_icon()

# 让计时显示一个好看的时间
p.window.update_time_display(18, 42)
p.window.update_progress(18 * 60 + 42, 25 * 60)
p.window.show()
app.processEvents()

# 1. 主窗口
p.window.grab().save(os.path.join(OUT, "main_work.png"))

# 2. 休息状态
p.window.set_mode(False)
p.window.set_theme("forest") if hasattr(p.window, "set_theme") else None
p.window.update_time_display(4, 16)
p.window.update_progress(4 * 60 + 16, 5 * 60)
app.processEvents()
p.window.grab().save(os.path.join(OUT, "main_break.png"))

# 2b. 浅色主题三态（白底配图用）
p.window.set_theme("light")
p.window.set_mode(True)
p.window.update_time_display(18, 42)
p.window.update_progress(18 * 60 + 42, 25 * 60)
app.processEvents()
p.window.grab().save(os.path.join(OUT, "light_work.png"))

p.window.set_mode(False)
p.window.update_time_display(4, 16)
p.window.update_progress(4 * 60 + 16, 5 * 60)
app.processEvents()
p.window.grab().save(os.path.join(OUT, "light_break.png"))

p.window.update_time_display(12, 5)
p.window.update_progress(12 * 60 + 5, 15 * 60)
app.processEvents()
p.window.grab().save(os.path.join(OUT, "light_longbreak.png"))

# 3. 右键菜单（真实构造，grab 不阻塞）
p.window.set_theme("deep_space") if hasattr(p.window, "set_theme") else None
menu = _TopmostMenu(p.window)
toggle = menu.addAction("⏸  暂停")
menu.addAction("↺  重置")
menu.addSeparator()
menu.addAction("🔄  连续专注")
menu.addSeparator()
menu.addAction("📊  今日统计")
menu.addAction("⚙  设置")
menu.addSeparator()
menu.addAction("✕  退出")
menu.show()
app.processEvents()
menu.grab().save(os.path.join(OUT, "menu.png"))
menu.hide()

# 4. 设置窗口
dlg = SettingsDialog(p.settings_manager)
dlg.show()
app.processEvents()
dlg.grab().save(os.path.join(OUT, "settings.png"))
dlg.hide()

# 5. 历史窗口
p.history_manager.add_record("work", 25)
hd = HistoryDialog(p.history_manager)
hd.show()
app.processEvents()
hd.grab().save(os.path.join(OUT, "history.png"))
hd.hide()

for name in sorted(os.listdir(OUT)):
    path = os.path.join(OUT, name)
    print(name, os.path.getsize(path))
print("captured to", OUT)
