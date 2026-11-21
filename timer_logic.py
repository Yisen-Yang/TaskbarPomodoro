import time
from enum import Enum
from PySide6.QtCore import QTimer, Signal, QObject


class TimerState(Enum):
    IDLE = 0
    RUNNING = 1
    PAUSED = 2
    COMPLETED = 3


class TimerMode(Enum):
    WORK = 0
    BREAK = 1
    LONG_BREAK = 2


class PomodoroTimer(QObject):
    time_updated = Signal(int, int)
    state_changed = Signal(TimerState)
    mode_changed = Signal(TimerMode)
    timer_completed = Signal(TimerMode)

    def __init__(self):
        super().__init__()
        self.work_minutes = 25
        self.break_minutes = 5
        self.long_break_minutes = 15
        self.long_break_interval = 4      # 每完成 N 个番茄进入长休息
        self.completed_count = 0          # 已完成的专注轮数（跨模式累计）

        self.current_mode = TimerMode.WORK
        self.current_state = TimerState.IDLE
        self.remaining_seconds = self.work_minutes * 60

        # ── 防漂移核心：用单调时钟记录截止时刻，而非每秒 -1 ──
        self._deadline = None             # time.monotonic() 绝对截止时刻
        self._paused_remaining = 0.0      # 暂停时累计的剩余秒数（浮点，保证精度）

        self.timer = QTimer()
        self.timer.setInterval(200)       # 200ms 刷新，显示更平滑，唤醒后快速追平
        self.timer.timeout.connect(self.on_timer_tick)

    # ── 时长配置 ────────────────────────────────────────────────
    def _duration_seconds(self, mode=None):
        mode = mode or self.current_mode
        if mode == TimerMode.WORK:
            return self.work_minutes * 60
        if mode == TimerMode.LONG_BREAK:
            return self.long_break_minutes * 60
        return self.break_minutes * 60

    def set_work_minutes(self, minutes):
        self.work_minutes = minutes
        if self.current_state == TimerState.IDLE and self.current_mode == TimerMode.WORK:
            self.remaining_seconds = minutes * 60
            self._paused_remaining = float(self.remaining_seconds)
            self.notify_time_update()

    def set_break_minutes(self, minutes):
        self.break_minutes = minutes
        if self.current_state == TimerState.IDLE and self.current_mode == TimerMode.BREAK:
            self.remaining_seconds = minutes * 60
            self._paused_remaining = float(self.remaining_seconds)
            self.notify_time_update()

    def set_long_break_minutes(self, minutes):
        self.long_break_minutes = minutes
        if self.current_state == TimerState.IDLE and self.current_mode == TimerMode.LONG_BREAK:
            self.remaining_seconds = minutes * 60
            self._paused_remaining = float(self.remaining_seconds)
            self.notify_time_update()

    def set_long_break_interval(self, count):
        self.long_break_interval = max(2, count)

    # ── 状态控制 ────────────────────────────────────────────────
    def start(self):
        if self.current_state == TimerState.COMPLETED:
            self.reset()
        if self.current_state == TimerState.RUNNING:
            return
        self.current_state = TimerState.RUNNING
        # 以当前剩余秒数为基准设定截止时刻（暂停后能无缝续接）
        self._deadline = time.monotonic() + self._paused_remaining
        self.state_changed.emit(self.current_state)
        self.timer.start()

    def pause(self):
        if self.current_state == TimerState.RUNNING:
            # 先按绝对时钟结算一次，避免暂停瞬间的偏差
            self._paused_remaining = max(0.0, self._deadline - time.monotonic())
            self.remaining_seconds = int(self._paused_remaining + 0.999)
            self.current_state = TimerState.PAUSED
            self.state_changed.emit(self.current_state)
            self.timer.stop()
            self.notify_time_update()

    def reset(self):
        self.timer.stop()
        self.current_state = TimerState.IDLE
        self.remaining_seconds = self._duration_seconds()
        self._paused_remaining = float(self.remaining_seconds)
        self._deadline = None
        self.state_changed.emit(self.current_state)
        self.notify_time_update()

    def toggle(self):
        if self.current_state == TimerState.RUNNING:
            self.pause()
        else:
            self.start()

    def switch_mode(self, mode):
        self.current_mode = mode
        self.mode_changed.emit(mode)
        self.reset()

    def cycle_mode(self):
        if self.current_mode == TimerMode.WORK:
            self.switch_mode(TimerMode.BREAK)
        else:
            self.switch_mode(TimerMode.WORK)

    def on_timer_tick(self):
        # 防御：定时器若在异常状态下仍触发，直接停下，避免 None 运算导致退出
        if self._deadline is None:
            self.timer.stop()
            return
        # 剩余时间始终由「截止时刻 - 当前时刻」推导，休眠/卡顿后自动追平
        remaining = max(0.0, self._deadline - time.monotonic())
        new_seconds = int(remaining + 0.999)  # 向上取整，显示从整数秒开始递减
        self._paused_remaining = remaining
        if new_seconds != self.remaining_seconds:
            self.remaining_seconds = new_seconds
            self.notify_time_update()
        if remaining <= 0:
            self.complete()

    def complete(self):
        self.timer.stop()
        self.current_state = TimerState.COMPLETED
        self.remaining_seconds = 0
        self._paused_remaining = 0.0
        self._deadline = None
        self.notify_time_update()
        self.state_changed.emit(self.current_state)
        self.timer_completed.emit(self.current_mode)

    def register_work_completed(self):
        """记录一次专注完成，返回本次结束后是否应进入长休息。"""
        self.completed_count += 1
        return self.completed_count % self.long_break_interval == 0

    def notify_time_update(self):
        minutes = self.remaining_seconds // 60
        seconds = self.remaining_seconds % 60
        self.time_updated.emit(minutes, seconds)

    def get_remaining_time(self):
        return self.remaining_seconds // 60, self.remaining_seconds % 60

    def is_running(self):
        return self.current_state == TimerState.RUNNING

    def get_state(self):
        return self.current_state

    def get_mode(self):
        return self.current_mode
