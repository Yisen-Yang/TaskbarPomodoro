from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QAction
from PySide6.QtCore import Signal

from app_icon import get_app_icon


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
        self.create_icon()
        self.create_menu()
        self.setToolTip("番茄钟")
        self.show()

    def create_icon(self):
        self.setIcon(get_app_icon())

    def create_menu(self):
        self.menu = QMenu()

        self.start_action = QAction("开始", self)
        self.start_action.triggered.connect(self.on_start_triggered)

        self.pause_action = QAction("暂停", self)
        self.pause_action.triggered.connect(self.on_pause_triggered)
        self.pause_action.setVisible(False)

        self.reset_action = QAction("重置", self)
        self.reset_action.triggered.connect(self.on_reset_triggered)

        self.menu.addSeparator()

        # 连续专注（可勾选）
        self.continuous_action = QAction("连续专注", self)
        self.continuous_action.setCheckable(True)
        self.continuous_action.triggered.connect(self.on_continuous_focus_triggered)

        self.today_stats_action = QAction("今日统计", self)
        self.today_stats_action.triggered.connect(self.on_today_stats_triggered)

        self.settings_action = QAction("设置", self)
        self.settings_action.triggered.connect(self.on_settings_triggered)

        self.history_action = QAction("历史记录", self)
        self.history_action.triggered.connect(self.on_history_triggered)

        self.toggle_window_action = QAction("隐藏窗口", self)
        self.toggle_window_action.triggered.connect(self.on_toggle_window_triggered)

        self.menu.addSeparator()

        self.exit_action = QAction("退出", self)
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

        self.setContextMenu(self.menu)

    def update_state(self, is_running):
        if is_running:
            self.start_action.setVisible(False)
            self.pause_action.setVisible(True)
            self.setToolTip("番茄钟 - 运行中")
        else:
            self.start_action.setVisible(True)
            self.pause_action.setVisible(False)
            self.setToolTip("番茄钟")

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
