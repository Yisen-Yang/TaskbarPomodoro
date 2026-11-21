import os

from PySide6.QtWidgets import (
    QDialog, QLabel, QSpinBox, QCheckBox,
    QPushButton, QVBoxLayout, QHBoxLayout, QGroupBox, QComboBox
)
from PySide6.QtCore import Qt, Signal

from theme import theme_keys, theme_label
from app_icon import get_app_icon
from platform_utils import set_auto_start
from i18n import i18n, tr, language_items
import sounds


class SettingsManager:
    def __init__(self):
        self.settings = {}
        self.load_defaults()
        self.load_settings()
        i18n.set_language(self.get('language') or 'system')

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
            'window_y': None,
            'theme': 'deep_space',
            # 默认：开始上行 / 结束下行
            'start_sound': 'start_up',
            'end_sound': 'end_down',
            # 老配置迁移标记（老版本开始/结束都是 classic）
            'sound_pair_v2': False,
            'language': 'system',
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

        # 一次性升级：老配置里两个音效都是 classic，换成方向上/下的默认对
        if (not self.settings.get('sound_pair_v2')
                and self.settings.get('start_sound') == 'classic'
                and self.settings.get('end_sound') == 'classic'):
            self.settings['start_sound'] = 'start_up'
            self.settings['end_sound'] = 'end_down'
            self.settings['sound_pair_v2'] = True
            self.save_settings()
        else:
            self.settings['sound_pair_v2'] = True

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
            elif key == 'language':
                i18n.set_language(value)

    def set_auto_start(self, enable):
        set_auto_start(enable)


class SettingsDialog(QDialog):
    settings_changed = Signal()

    def __init__(self, settings_manager, parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self._initial_language = settings_manager.get('language') or 'system'
        self.setWindowTitle(tr("Settings"))
        self.setWindowIcon(get_app_icon())
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
            QSpinBox, QComboBox {
                padding: 4px 8px;
                border: 1px solid #c0c0c8;
                border-radius: 4px;
                background-color: white;
                min-height: 26px;
                font-size: 13px;
            }
            QSpinBox:focus, QComboBox:focus {
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
        self.time_group = QGroupBox(tr("Timer"))
        time_layout = QVBoxLayout(self.time_group)
        time_layout.setSpacing(12)

        self.work_label = QLabel(tr("Work (minutes):"))
        self.work_spin = QSpinBox()
        self.work_spin.setRange(1, 180)
        self.work_spin.setValue(self.settings_manager.get('work_minutes'))
        work_layout = QHBoxLayout()
        work_layout.addWidget(self.work_label)
        work_layout.addWidget(self.work_spin)
        time_layout.addLayout(work_layout)

        self.break_label = QLabel(tr("Short break (minutes):"))
        self.break_spin = QSpinBox()
        self.break_spin.setRange(1, 90)
        self.break_spin.setValue(self.settings_manager.get('break_minutes'))
        break_layout = QHBoxLayout()
        break_layout.addWidget(self.break_label)
        break_layout.addWidget(self.break_spin)
        time_layout.addLayout(break_layout)

        self.long_break_label = QLabel(tr("Long break (minutes):"))
        self.long_break_spin = QSpinBox()
        self.long_break_spin.setRange(1, 120)
        self.long_break_spin.setValue(self.settings_manager.get('long_break_minutes'))
        long_break_layout = QHBoxLayout()
        long_break_layout.addWidget(self.long_break_label)
        long_break_layout.addWidget(self.long_break_spin)
        time_layout.addLayout(long_break_layout)

        self.interval_label = QLabel(tr("Long break every N pomodoros:"))
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(2, 10)
        self.interval_spin.setValue(self.settings_manager.get('long_break_interval'))
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(self.interval_label)
        interval_layout.addWidget(self.interval_spin)
        time_layout.addLayout(interval_layout)

        layout.addWidget(self.time_group)

        # ── 专注模式 ──
        self.mode_group = QGroupBox(tr("Focus mode"))
        mode_layout = QVBoxLayout(self.mode_group)
        mode_layout.setSpacing(8)
        self.continuous_check = QCheckBox(
            tr("Continuous focus (auto cycle work + break until paused)"))
        self.continuous_check.setChecked(self.settings_manager.get('continuous_focus'))
        mode_layout.addWidget(self.continuous_check)
        layout.addWidget(self.mode_group)

        # ── 外观主题 ──
        self.theme_group = QGroupBox(tr("Appearance"))
        theme_layout = QHBoxLayout(self.theme_group)
        self.theme_label_widget = QLabel(tr("Theme:"))
        self.theme_combo = QComboBox()
        cur_theme = self.settings_manager.get('theme') or 'deep_space'
        for key in theme_keys():
            self.theme_combo.addItem(theme_label(key), key)
        self.theme_combo.setCurrentIndex(max(0, self.theme_combo.findData(cur_theme)))
        theme_layout.addWidget(self.theme_label_widget)
        theme_layout.addWidget(self.theme_combo)
        layout.addWidget(self.theme_group)

        # ── 声音设置 ──
        self.sound_group = QGroupBox(tr("Sound"))
        sound_layout = QVBoxLayout(self.sound_group)
        sound_layout.setSpacing(8)

        self.sound_check = QCheckBox(tr("Enable sound"))
        self.sound_check.setChecked(self.settings_manager.get('sound_enabled'))
        sound_layout.addWidget(self.sound_check)

        self.start_label = QLabel(tr("Start / next round:"))
        self.start_sound_combo = QComboBox()
        for label, key in sounds.display_names():
            self.start_sound_combo.addItem(label, key)
        cur_start = self.settings_manager.get('start_sound') or 'start_up'
        self.start_sound_combo.setCurrentIndex(
            max(0, self.start_sound_combo.findData(cur_start)))
        start_row = QHBoxLayout()
        start_row.addWidget(self.start_label)
        start_row.addWidget(self.start_sound_combo)
        sound_layout.addLayout(start_row)

        self.end_label = QLabel(tr("Focus end:"))
        self.end_sound_combo = QComboBox()
        for label, key in sounds.display_names():
            self.end_sound_combo.addItem(label, key)
        cur_end = self.settings_manager.get('end_sound') or 'end_down'
        self.end_sound_combo.setCurrentIndex(
            max(0, self.end_sound_combo.findData(cur_end)))
        end_row = QHBoxLayout()
        end_row.addWidget(self.end_label)
        end_row.addWidget(self.end_sound_combo)
        sound_layout.addLayout(end_row)

        layout.addWidget(self.sound_group)

        # ── 选项（含语言）──
        self.option_group = QGroupBox(tr("Options"))
        option_layout = QVBoxLayout(self.option_group)
        option_layout.setSpacing(8)

        self.auto_start_check = QCheckBox(tr("Run at startup"))
        self.auto_start_check.setChecked(self.settings_manager.get('auto_start_on_windows'))
        option_layout.addWidget(self.auto_start_check)

        self.language_label = QLabel(tr("Language:"))
        self.language_combo = QComboBox()
        for label, code in language_items():
            self.language_combo.addItem(label, code)
        self.language_combo.setCurrentIndex(max(0, self.language_combo.findData(
            self.settings_manager.get('language') or 'system')))
        self.language_combo.currentIndexChanged.connect(self.on_language_changed)
        language_row = QHBoxLayout()
        language_row.addWidget(self.language_label)
        language_row.addWidget(self.language_combo)
        option_layout.addLayout(language_row)

        layout.addWidget(self.option_group)

        # ── 按钮 ──
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.ok_btn = QPushButton(tr("OK"))
        self.ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.ok_btn)
        self.cancel_btn = QPushButton(tr("Cancel"))
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)
        self.adjustSize()

    @staticmethod
    def _rebuild_combo(combo, items, current):
        combo.blockSignals(True)
        combo.clear()
        for label, value in items:
            combo.addItem(label, value)
        combo.setCurrentIndex(max(0, combo.findData(current)))
        combo.blockSignals(False)

    def retranslate(self):
        """切换语言时即时刷新当前已打开的设置窗口。"""
        self.setWindowTitle(tr("Settings"))
        self.time_group.setTitle(tr("Timer"))
        self.work_label.setText(tr("Work (minutes):"))
        self.break_label.setText(tr("Short break (minutes):"))
        self.long_break_label.setText(tr("Long break (minutes):"))
        self.interval_label.setText(tr("Long break every N pomodoros:"))
        self.mode_group.setTitle(tr("Focus mode"))
        self.continuous_check.setText(
            tr("Continuous focus (auto cycle work + break until paused)"))
        self.theme_group.setTitle(tr("Appearance"))
        self.theme_label_widget.setText(tr("Theme:"))
        self.sound_group.setTitle(tr("Sound"))
        self.sound_check.setText(tr("Enable sound"))
        self.start_label.setText(tr("Start / next round:"))
        self.end_label.setText(tr("Focus end:"))
        self.option_group.setTitle(tr("Options"))
        self.auto_start_check.setText(tr("Run at startup"))
        self.language_label.setText(tr("Language:"))
        self.ok_btn.setText(tr("OK"))
        self.cancel_btn.setText(tr("Cancel"))

        self._rebuild_combo(
            self.theme_combo,
            [(theme_label(key), key) for key in theme_keys()],
            self.theme_combo.currentData())
        sound_items = sounds.display_names()
        self._rebuild_combo(self.start_sound_combo, sound_items,
                            self.start_sound_combo.currentData())
        self._rebuild_combo(self.end_sound_combo, sound_items,
                            self.end_sound_combo.currentData())
        self._rebuild_combo(self.language_combo, language_items(),
                            self.language_combo.currentData())
        self.adjustSize()

    def on_language_changed(self):
        i18n.set_language(self.language_combo.currentData() or 'system')
        self.retranslate()

    def accept(self):
        self.settings_manager.set('work_minutes', self.work_spin.value())
        self.settings_manager.set('break_minutes', self.break_spin.value())
        self.settings_manager.set('long_break_minutes', self.long_break_spin.value())
        self.settings_manager.set('long_break_interval', self.interval_spin.value())
        self.settings_manager.set('continuous_focus', self.continuous_check.isChecked())
        self.settings_manager.set('sound_enabled', self.sound_check.isChecked())
        self.settings_manager.set('auto_start_on_windows', self.auto_start_check.isChecked())
        self.settings_manager.set('theme', self.theme_combo.currentData())
        self.settings_manager.set('start_sound', self.start_sound_combo.currentData())
        self.settings_manager.set('end_sound', self.end_sound_combo.currentData())
        self.settings_manager.set('language', self.language_combo.currentData() or 'system')
        self.settings_changed.emit()
        super().accept()

    def reject(self):
        i18n.set_language(self._initial_language)
        super().reject()
