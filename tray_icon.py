from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, Signal

from app_icon import get_app_icon
from i18n import tr
from ui_style import menu_stylesheet


class TrayIcon(QSystemTrayIcon):
    start_requested = Signal()
    pause_requested = Signal()
    reset_requested = Signal()
    settings_requested = Signal()
    history_requested = Signal()
    today_stats_requested = Signal()
    continuous_focus_toggled = Signal(bool)
    toggle_window_requested = Signal()
    exit_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._countdown_text = ''
        self._theme_key = 'deep_space'
        self._running = False
        self.create_icon()
        self.create_menu()
        self._refresh_tooltip()
        self.show()

    def create_icon(self):
        self.setIcon(get_app_icon())

    def _refresh_tooltip(self):
        text = (tr("Pomodoro {time}", time=self._countdown_text)
                if self._countdown_text else tr("Pomodoro"))
        if self._running:
            text += " - " + tr("Running")
        self.setToolTip(text)

    def update_countdown(self, text):
        """更新 tooltip 中的倒计时文字。"""
        self._countdown_text = text or ''
        self._refresh_tooltip()

    def create_menu(self):
        self.menu = QMenu()

        self.start_action = QAction(tr("Start"), self)
        self.start_action.triggered.connect(self.on_start_triggered)

        self.pause_action = QAction(tr("Pause"), self)
        self.pause_action.triggered.connect(self.on_pause_triggered)
        self.pause_action.setVisible(False)

        self.reset_action = QAction(tr("Reset"), self)
        self.reset_action.triggered.connect(self.on_reset_triggered)

        self.menu.addSeparator()

        # 连续专注（可勾选）
        self.continuous_action = QAction(tr("Continuous focus"), self)
        self.continuous_action.setCheckable(True)
        self.continuous_action.triggered.connect(self.on_continuous_focus_triggered)

        self.today_stats_action = QAction(tr("Today's stats"), self)
        self.today_stats_action.triggered.connect(self.on_today_stats_triggered)

        self.settings_action = QAction(tr("Settings"), self)
        self.settings_action.triggered.connect(self.on_settings_triggered)

        self.history_action = QAction(tr("History"), self)
        self.history_action.triggered.connect(self.on_history_triggered)

        self.toggle_window_action = QAction(tr("Hide window"), self)
        self.toggle_window_action.triggered.connect(self.on_toggle_window_triggered)

        self.menu.addSeparator()

        self.exit_action = QAction(tr("Exit"), self)
        self.exit_action.triggered.connect(self.on_exit_triggered)

        self.menu.addActions([
            self.start_action,
            self.pause_action,
            self.reset_action
        ])
        self.menu.addSeparator()
        self.menu.addAction(self.continuous_action)
        self.menu.addAction(self.today_stats_action)
        self.menu.addSeparator()
        self.menu.addActions([
            self.settings_action,
            self.history_action,
            self.toggle_window_action
        ])
        self.menu.addSeparator()
        self.menu.addAction(self.exit_action)

        self.menu.setStyleSheet(menu_stylesheet(self._theme_key))
        self.setContextMenu(self.menu)

    def set_theme(self, theme_key):
        """切换主题时同步托盘菜单样式（不影响计时）。"""
        self._theme_key = theme_key
        self.menu.setStyleSheet(menu_stylesheet(theme_key))

    def retranslate(self):
        """切换界面语言后刷新托盘菜单与提示文字。"""
        self.start_action.setText(tr("Start"))
        self.pause_action.setText(tr("Pause"))
        self.reset_action.setText(tr("Reset"))
        self.continuous_action.setText(tr("Continuous focus"))
        self.today_stats_action.setText(tr("Today's stats"))
        self.settings_action.setText(tr("Settings"))
        self.history_action.setText(tr("History"))
        self.toggle_window_action.setText(tr("Hide window"))
        self.exit_action.setText(tr("Exit"))
        self._refresh_tooltip()

    def update_state(self, is_running):
        self._running = is_running
        if is_running:
            self.start_action.setVisible(False)
            self.pause_action.setVisible(True)
        else:
            self.start_action.setVisible(True)
            self.pause_action.setVisible(False)
        self._refresh_tooltip()

    def update_continuous_focus(self, checked):
        """从外部更新连续专注菜单状态"""
        self.continuous_action.blockSignals(True)
        self.continuous_action.setChecked(checked)
        self.continuous_action.blockSignals(False)

    def on_start_triggered(self):
        self.start_action.setVisible(False)
        self.pause_action.setVisible(True)
        self.start_requested.emit()

    def on_pause_triggered(self):
        self.pause_action.setVisible(False)
        self.start_action.setVisible(True)
        self.pause_requested.emit()

    def on_reset_triggered(self):
        self.reset_requested.emit()

    def on_continuous_focus_triggered(self):
        self.continuous_focus_toggled.emit(self.continuous_action.isChecked())

    def on_today_stats_triggered(self):
        self.today_stats_requested.emit()

    def on_settings_triggered(self):
        self.settings_requested.emit()

    def on_history_triggered(self):
        self.history_requested.emit()

    def on_toggle_window_triggered(self):
        self.toggle_window_requested.emit()

    def on_exit_triggered(self):
        self.exit_requested.emit()
