import sys
import os

from PySide6.QtWidgets import QApplication, QMessageBox, QSystemTrayIcon
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

from appbar_window import PomodoroWindow
from app_icon import get_app_icon
from timer_logic import PomodoroTimer, TimerMode, TimerState
from settings import SettingsManager, SettingsDialog
from tray_icon import TrayIcon
from history_manager import HistoryManager
from history_dialog import HistoryDialog
from platform_utils import play_sound_file, IS_MAC, IS_LINUX
import sounds


def get_sound_path(filename):
    """获取音效文件路径，同时兼容开发环境和打包后的 EXE"""
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, 'sound', filename)


def resolve_sound(num):
    """旧接口兼容：1/2 映射到设置里选择的开始/结束音效。"""
    return None, None  # 播放逻辑已改用 play_sound_key，不再使用此函数


def resolve_sound_key(key):
    """按音效 key 解析出 (完整路径, MCI 类型)，找不到返回 (None, None)。"""
    filename, mci_type = sounds.resolve(key)
    path = get_sound_path(filename)
    if os.path.exists(path):
        return path, mci_type
    # 回退到经典音效
    fallback, ftype = sounds.resolve('classic')
    path = get_sound_path(fallback)
    if os.path.exists(path):
        return path, ftype
    return None, None


class PomodoroApp:
    def __init__(self):
        self.settings_manager = SettingsManager()
        self.history_manager = HistoryManager()
        self.timer = PomodoroTimer()
        self.window = None
        self.tray_icon = None
        self.settings_dialog = None
        self.history_dialog = None
        self.current_total_seconds = 25 * 60

        self.setup_timer()

    def setup_timer(self):
        work_minutes = self.settings_manager.get('work_minutes')
        break_minutes = self.settings_manager.get('break_minutes')
        long_break_minutes = self.settings_manager.get('long_break_minutes')
        long_break_interval = self.settings_manager.get('long_break_interval')

        self.timer.set_work_minutes(work_minutes)
        self.timer.set_break_minutes(break_minutes)
        self.timer.set_long_break_minutes(long_break_minutes)
        self.timer.set_long_break_interval(long_break_interval)

        self.current_total_seconds = work_minutes * 60

        self.timer.time_updated.connect(self.on_time_updated)
        self.timer.state_changed.connect(self.on_state_changed)
        self.timer.mode_changed.connect(self.on_mode_changed)
        self.timer.timer_completed.connect(self.on_timer_completed)

    def create_window(self):
        self.window = PomodoroWindow(self.settings_manager)

        self.window.start_pause_clicked.connect(self.on_start_pause)
        self.window.reset_clicked.connect(self.on_reset)
        self.window.preset_changed.connect(self.on_preset_changed)

        # 右键菜单信号
        self.window.settings_requested.connect(self.on_settings)
        self.window.stats_requested.connect(self.on_today_stats)
        self.window.continuous_focus_toggled.connect(self.on_continuous_focus_toggled)
        self.window.hide_requested.connect(self.on_toggle_window)
        self.window.exit_requested.connect(self.on_exit)

        # 同步预设下拉框
        work = self.settings_manager.get('work_minutes')
        brk = self.settings_manager.get('break_minutes')
        self.window.update_preset_from_settings(work, brk)

        minutes, seconds = self.timer.get_remaining_time()
        self.window.update_time_display(minutes, seconds)
        self.window.update_progress(self.current_total_seconds, self.current_total_seconds)

        # macOS：以顶部菜单栏为主，默认隐藏浮动窗口（点菜单『显示窗口』才弹出）
        if IS_MAC:
            if getattr(self, '_mac_window_hidden', None) is None:
                self._mac_window_hidden = True
            if not self._mac_window_hidden:
                self.window.show()
        else:
            self.window.show()

    def create_tray_icon(self):
        self.tray_icon = TrayIcon()
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.start_requested.connect(self.on_start)
        self.tray_icon.pause_requested.connect(self.on_pause)
        self.tray_icon.reset_requested.connect(self.on_reset)
        self.tray_icon.settings_requested.connect(self.on_settings)
        self.tray_icon.history_requested.connect(self.on_history)
        self.tray_icon.today_stats_requested.connect(self.on_today_stats)
        self.tray_icon.continuous_focus_toggled.connect(self.on_continuous_focus_toggled)
        self.tray_icon.toggle_window_requested.connect(self.on_toggle_window)
        self.tray_icon.exit_requested.connect(self.on_exit)

        # 同步连续专注初始状态
        continuous = self.settings_manager.get('continuous_focus')
        self.tray_icon.update_continuous_focus(continuous)

        # macOS：窗口默认隐藏，托盘菜单文字改为『显示窗口』
        if IS_MAC and getattr(self, '_mac_window_hidden', False):
            self.tray_icon.toggle_window_action.setText("显示窗口")

    # ── 计时器回调 ────────────────────────────────────────────────
    def on_time_updated(self, minutes, seconds):
        if self.window:
            self.window.update_time_display(minutes, seconds)
            remaining = minutes * 60 + seconds
            self.window.update_progress(remaining, self.current_total_seconds)
        if self.tray_icon:
            self.tray_icon.update_countdown(f"{minutes:02d}:{seconds:02d}")

    def on_state_changed(self, state):
        if self.window:
            self.window.set_running_state(state == TimerState.RUNNING)
        if self.tray_icon:
            self.tray_icon.update_state(state == TimerState.RUNNING)

    def on_mode_changed(self, mode):
        if self.window:
            self.window.set_mode(mode == TimerMode.WORK)

        if mode == TimerMode.WORK:
            self.current_total_seconds = self.timer.work_minutes * 60
        elif mode == TimerMode.LONG_BREAK:
            self.current_total_seconds = self.timer.long_break_minutes * 60
        else:
            self.current_total_seconds = self.timer.break_minutes * 60

        minutes, seconds = self.timer.get_remaining_time()
        self.on_time_updated(minutes, seconds)

    def on_timer_completed(self, mode):
        continuous = self.settings_manager.get('continuous_focus')

        # ── 专注结束：记录、判断长休息 ────────────────────────
        if mode == TimerMode.WORK:
            try:
                self.history_manager.add_record('work', self.timer.work_minutes)
            except Exception:
                pass

            is_long = self.timer.register_work_completed()
            next_mode = TimerMode.LONG_BREAK if is_long else TimerMode.BREAK

            if self.settings_manager.get('sound_enabled'):
                self.play_sound('end')
            try:
                self.show_notification(mode, next_mode)
            except Exception:
                pass

            # 工作→（短/长）休息：始终自动开始
            self.timer.switch_mode(next_mode)
            self.timer.start()

        # ── 休息结束（短休息 或 长休息）────────────────────────
        else:
            mode_str = 'break'
            duration = (self.timer.long_break_minutes if mode == TimerMode.LONG_BREAK
                        else self.timer.break_minutes)
            try:
                self.history_manager.add_record(mode_str, duration)
            except Exception:
                pass

            # 休息结束 + 连续专注 → 播放开始音效并自动进入下一轮
            if continuous and self.settings_manager.get('sound_enabled'):
                self.play_sound('start')
            try:
                self.show_notification(mode, TimerMode.WORK)
            except Exception:
                pass

            self.timer.switch_mode(TimerMode.WORK)
            if continuous:
                self.timer.start()
            # 非连续：回到 idle 初始状态

    # ── 声音 / 通知 ──────────────────────────────────────────────
    def play_sound(self, kind):
        """跨平台播放提示音。
        kind='start' 用设置里的开始音效，'end' 用结束音效。"""
        try:
            key = self.settings_manager.get(f'{kind}_sound')
            path, mci_type = resolve_sound_key(key)
            if not path:
                return
            play_sound_file(path, mci_type)
        except Exception:
            pass

    def play_sound_file(self, file_num):
        """旧调用兼容：1->start, 2->end。"""
        self.play_sound('start' if file_num == 1 else 'end')

    def show_notification(self, mode, next_mode=None):
        continuous = self.settings_manager.get('continuous_focus')
        if mode == TimerMode.WORK:
            title = "🍅 专注完成！"
            if next_mode == TimerMode.LONG_BREAK:
                message = f"已完成一轮，好好休息 {self.timer.long_break_minutes} 分钟吧！"
            else:
                message = "短暂休息一下，准备下一轮专注。"
        elif mode == TimerMode.LONG_BREAK:
            title = "长休息结束！"
            message = "准备开始下一轮专注！" if continuous else "准备开始专注！"
        else:
            title = "休息结束！"
            message = "准备开始下一轮专注！" if continuous else "准备开始专注！"

        if self.tray_icon:
            self.tray_icon.showMessage(title, message, QSystemTrayIcon.MessageIcon.Information, 3000)

    # ── 按钮事件 ──────────────────────────────────────────────────
    def on_start_pause(self):
        was_idle = (self.timer.get_state() == TimerState.IDLE)
        self.timer.toggle()
        # 从 IDLE 开始工作模式时播放开始音效
        if was_idle and self.timer.is_running() and self.timer.get_mode() == TimerMode.WORK:
            if self.settings_manager.get('sound_enabled'):
                self.play_sound('start')

    def on_reset(self):
        self.timer.reset()

    def on_start(self):
        was_idle = (self.timer.get_state() == TimerState.IDLE)
        self.timer.start()
        if was_idle and self.timer.get_mode() == TimerMode.WORK:
            if self.settings_manager.get('sound_enabled'):
                self.play_sound('start')

    def on_pause(self):
        self.timer.pause()

    # ── 预设切换 ──────────────────────────────────────────────────
    def on_preset_changed(self, text):
        presets = {
            "5/1": (5, 1), "15/5": (15, 5),
            "25/5": (25, 5), "30/5": (30, 5)
        }

        if text in presets:
            work, break_time = presets[text]
            self.settings_manager.set('work_minutes', work)
            self.settings_manager.set('break_minutes', break_time)

            self.timer.set_work_minutes(work)
            self.timer.set_break_minutes(break_time)

            # 关键：更新 current_total_seconds 以保证圆环比例正确
            mode = self.timer.get_mode()
            if mode == TimerMode.WORK:
                self.current_total_seconds = work * 60
            elif mode == TimerMode.LONG_BREAK:
                self.current_total_seconds = self.timer.long_break_minutes * 60
            else:
                self.current_total_seconds = break_time * 60

            self.timer.reset()

    # ── 设置 ──────────────────────────────────────────────────────
    def on_settings(self):
        # 暂停 topmost timer，防止 50ms 刷新导致对话框闪动
        if self.window:
            self.window.topmost_timer.stop()

        self.settings_dialog = SettingsDialog(self.settings_manager)
        self.settings_dialog.settings_changed.connect(self.on_settings_changed)
        self.settings_dialog.exec()

        if self.window:
            self.window.topmost_timer.start()

    def on_settings_changed(self):
        work_minutes = self.settings_manager.get('work_minutes')
        break_minutes = self.settings_manager.get('break_minutes')
        long_break_minutes = self.settings_manager.get('long_break_minutes')
        long_break_interval = self.settings_manager.get('long_break_interval')

        self.timer.set_work_minutes(work_minutes)
        self.timer.set_break_minutes(break_minutes)
        self.timer.set_long_break_minutes(long_break_minutes)
        self.timer.set_long_break_interval(long_break_interval)

        # 关键修复：更新 current_total_seconds，否则圆环比例错误
        mode = self.timer.get_mode()
        if mode == TimerMode.WORK:
            self.current_total_seconds = work_minutes * 60
        elif mode == TimerMode.LONG_BREAK:
            self.current_total_seconds = long_break_minutes * 60
        else:
            self.current_total_seconds = break_minutes * 60

        # 始终重置：让界面显示新设定的时间
        self.timer.reset()

        # 更新窗口显示
        if self.window:
            # 应用新主题（即时生效）
            self.window.set_theme(self.settings_manager.get('theme'))
            minutes, seconds = self.timer.get_remaining_time()
            self.window.update_time_display(minutes, seconds)
            self.window.update_progress(
                minutes * 60 + seconds,
                self.current_total_seconds
            )
            # 同步预设下拉框
            self.window.update_preset_from_settings(work_minutes, break_minutes)

        # 同步连续专注菜单状态
        continuous = self.settings_manager.get('continuous_focus')
        if self.tray_icon:
            self.tray_icon.update_continuous_focus(continuous)

    # ── 连续专注切换 ──────────────────────────────────────────────
    def on_continuous_focus_toggled(self, checked):
        self.settings_manager.set('continuous_focus', checked)
        # 同步两个菜单的显示状态
        if self.tray_icon:
            self.tray_icon.update_continuous_focus(checked)

    # ── 今日统计 ──────────────────────────────────────────────────
    def on_today_stats(self):
        if self.window:
            self.window.topmost_timer.stop()

        today_count = self.history_manager.get_today_pomodoros()
        today_work = self.history_manager.get_today_work_minutes()
        today_break = self.history_manager.get_today_break_minutes()
        total_work = self.history_manager.get_total_work_minutes()

        msg = QMessageBox()
        msg.setWindowTitle("今日统计")
        msg.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        msg.setIcon(QMessageBox.Information)
        msg.setText(
            f"🍅 今日专注：{today_work} 分钟\n"
            f"✅ 完成番茄钟：{today_count} 次\n"
            f"☕ 今日休息：{today_break} 分钟\n"
            f"📊 累计专注：{total_work} 分钟"
        )
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()

        if self.window:
            self.window.topmost_timer.start()

    # ── 历史记录 ──────────────────────────────────────────────────
    def on_history(self):
        if self.window:
            self.window.topmost_timer.stop()

        self.history_dialog = HistoryDialog(self.history_manager)
        self.history_dialog.setWindowFlags(
            self.history_dialog.windowFlags() | Qt.WindowStaysOnTopHint
        )
        self.history_dialog.exec()

        if self.window:
            self.window.topmost_timer.start()

    # ── 窗口显隐 ──────────────────────────────────────────────────
    def on_toggle_window(self):
        if self.window:
            if self.window.isVisible():
                self.window.hide()
                self._mac_window_hidden = True
                if self.tray_icon:
                    self.tray_icon.toggle_window_action.setText("显示窗口")
            else:
                self.window.show()
                self._mac_window_hidden = False
                if self.tray_icon:
                    self.tray_icon.toggle_window_action.setText("隐藏窗口")

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.on_start_pause()

    def on_exit(self):
        if self.window:
            self.window.save_position()
            self.window.close()
        QApplication.quit()


def main():
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setWindowIcon(get_app_icon())

    font = QFont("Segoe UI", 9)
    app.setFont(font)

    pomodoro = PomodoroApp()
    pomodoro.create_window()
    pomodoro.create_tray_icon()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
