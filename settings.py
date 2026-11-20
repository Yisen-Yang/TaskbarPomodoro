import os
import sys
import winreg

from PySide6.QtWidgets import (
    QDialog, QLabel, QSpinBox, QCheckBox,
    QPushButton, QVBoxLayout, QHBoxLayout, QGroupBox
)
from PySide6.QtCore import Qt, Signal


class SettingsManager:
    def __init__(self):
        self.settings = {}
        self.load_defaults()
        self.load_settings()

    def load_defaults(self):
        self.settings = {
            'work_minutes': 25,
            'break_minutes': 5,
            'long_break_minutes': 15,
            'long_break_interval': 4,
            'auto_start': False,
            'sound_enabled': True,
            'auto_start_on_windows': False,
            'continuous_focus': False,
            'window_x': None,
            'window_y': None
        }

    def load_settings(self):
        try:
            config_path = self.get_config_path()
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip()

                            if key in self.settings:
                                if isinstance(self.settings[key], bool):
                                    self.settings[key] = value.lower() == 'true'
                                elif isinstance(self.settings[key], int):
                                    try:
                                        self.settings[key] = int(value)
                                    except ValueError:
                                        pass
                                elif isinstance(self.settings[key], str):
                                    self.settings[key] = value
        except Exception:
            pass

    def save_settings(self):
        try:
            config_path = self.get_config_path()
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w', encoding='utf-8') as f:
                for key, value in self.settings.items():
                    if isinstance(value, bool):
                        f.write(f"{key}={str(value).lower()}\n")
                    elif value is None:
                        f.write(f"{key}=\n")
                    else:
                        f.write(f"{key}={value}\n")
        except Exception:
            pass

    def get_config_path(self):
        app_data = os.environ.get('APPDATA', os.path.expanduser('~'))
        return os.path.join(app_data, 'PomodoroTaskbar', 'settings.ini')

    def get(self, key):
        return self.settings.get(key)

    def set(self, key, value):
        if key in self.settings:
            self.settings[key] = value
            self.save_settings()
            if key == 'auto_start_on_windows':
                self.set_auto_start(value)

    def set_auto_start(self, enable):
        try:
            key_path = r'Software\Microsoft\Windows\CurrentVersion\Run'
            app_name = 'PomodoroTaskbar'

            if enable:
                exe_path = sys.executable if getattr(sys, 'frozen', False) else sys.argv[0]
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
                    winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, exe_path)
            else:
                try:
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
                        winreg.DeleteValue(key, app_name)
                except FileNotFoundError:
                    pass
        except Exception:
            pass


class SettingsDialog(QDialog):
    settings_changed = Signal()

    def __init__(self, settings_manager, parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.setWindowTitle("设置")
        # 独立顶层窗口 + 置顶，避免被主窗口的 50ms topmost 抢占导致闪动
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint)
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.setMinimumSize(380, 0)
        self.init_ui()

    def init_ui(self):
        # 实色背景，避免透明继承
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f8;
            }
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 1px solid #d0d0d8;
                border-radius: 8px;
                margin-top: 12px;
                padding: 16px 8px 8px 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px;
            }
            QLabel {
                font-size: 13px;
                color: #333;
            }
            QSpinBox {
                padding: 4px 8px;
                border: 1px solid #c0c0c8;
                border-radius: 4px;
                background-color: white;
                min-height: 26px;
                font-size: 13px;
            }
            QSpinBox:focus {
                border: 2px solid #6a8caf;
            }
            QPushButton {
                padding: 6px 20px;
                border: 1px solid #b0b0b8;
                border-radius: 6px;
                background-color: white;
                min-width: 70px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #e8e8f0;
            }
            QPushButton:pressed {
                background-color: #d0d0d8;
            }
            QCheckBox {
                font-size: 13px;
                spacing: 8px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        # ── 时间设置 ──
        time_group = QGroupBox("时间设置")
        time_layout = QVBoxLayout(time_group)
        time_layout.setSpacing(12)

        work_layout = QHBoxLayout()
        work_layout.addWidget(QLabel("工作时长 (分钟):"))
        self.work_spin = QSpinBox()
        self.work_spin.setRange(1, 180)
        self.work_spin.setValue(self.settings_manager.get('work_minutes'))
        work_layout.addWidget(self.work_spin)
        time_layout.addLayout(work_layout)

        break_layout = QHBoxLayout()
        break_layout.addWidget(QLabel("短休息时长 (分钟):"))
        self.break_spin = QSpinBox()
        self.break_spin.setRange(1, 90)
        self.break_spin.setValue(self.settings_manager.get('break_minutes'))
        break_layout.addWidget(self.break_spin)
        time_layout.addLayout(break_layout)

        long_break_layout = QHBoxLayout()
        long_break_layout.addWidget(QLabel("长休息时长 (分钟):"))
        self.long_break_spin = QSpinBox()
        self.long_break_spin.setRange(1, 120)
        self.long_break_spin.setValue(self.settings_manager.get('long_break_minutes'))
        long_break_layout.addWidget(self.long_break_spin)
        time_layout.addLayout(long_break_layout)

        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("每几个番茄长休息:"))
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(2, 10)
        self.interval_spin.setValue(self.settings_manager.get('long_break_interval'))
        interval_layout.addWidget(self.interval_spin)
        time_layout.addLayout(interval_layout)

        layout.addWidget(time_group)

        # ── 专注模式 ──
        mode_group = QGroupBox("专注模式")
        mode_layout = QVBoxLayout(mode_group)
        mode_layout.setSpacing(8)

        self.continuous_check = QCheckBox("连续专注（工作+休息自动循环，直到手动暂停）")
        self.continuous_check.setChecked(self.settings_manager.get('continuous_focus'))
        mode_layout.addWidget(self.continuous_check)

        layout.addWidget(mode_group)

        # ── 声音设置 ──
        sound_group = QGroupBox("声音设置")
        sound_layout = QVBoxLayout(sound_group)
        sound_layout.setSpacing(8)

        self.sound_check = QCheckBox("启用声音提示（内置提示音，可在 sound 目录自定义 1.mp3/2.mp3）")
        self.sound_check.setChecked(self.settings_manager.get('sound_enabled'))
        sound_layout.addWidget(self.sound_check)

        layout.addWidget(sound_group)

        # ── 选项 ──
        option_group = QGroupBox("选项")
        option_layout = QVBoxLayout(option_group)
        option_layout.setSpacing(8)

        self.auto_start_check = QCheckBox("开机自启")
        self.auto_start_check.setChecked(self.settings_manager.get('auto_start_on_windows'))
        option_layout.addWidget(self.auto_start_check)

        layout.addWidget(option_group)

        # ── 按钮 ──
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)

        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)
        self.adjustSize()

    def accept(self):
        self.settings_manager.set('work_minutes', self.work_spin.value())
        self.settings_manager.set('break_minutes', self.break_spin.value())
        self.settings_manager.set('long_break_minutes', self.long_break_spin.value())
        self.settings_manager.set('long_break_interval', self.interval_spin.value())
        self.settings_manager.set('continuous_focus', self.continuous_check.isChecked())
        self.settings_manager.set('sound_enabled', self.sound_check.isChecked())
        self.settings_manager.set('auto_start_on_windows', self.auto_start_check.isChecked())
        self.settings_changed.emit()
        super().accept()
