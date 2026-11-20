"""timer_logic 纯逻辑单元测试。

不依赖 GUI 事件循环：用极简 fake 替换 PySide6 的信号与定时器，
直接验证计时状态机、防漂移与长休息间隔逻辑。

运行：python -m unittest tests.test_timer_logic
"""
import sys
import time
import types
import unittest

# ── 用 fake 模块隔离 PySide6，使测试可在无 GUI 环境运行 ──────────
class FakeSignal:
    def __init__(self, *args):
        self._slots = []

    def connect(self, slot):
        self._slots.append(slot)

    def emit(self, *args):
        for slot in self._slots:
            slot(*args)


class FakeQTimer:
    def __init__(self):
        self._timeout = FakeSignal()

    def setInterval(self, ms):
        self.interval = ms

    @property
    def timeout(self):
        return self._timeout

    def start(self):
        self.active = True

    def stop(self):
        self.active = False


_qtcore = types.ModuleType("PySide6.QtCore")
_qtcore.Signal = FakeSignal
_qtcore.QObject = type("QObject", (), {"__init__": lambda self: None})
_qtcore.QTimer = FakeQTimer
_pyside = types.ModuleType("PySide6")
_pyside.QtCore = _qtcore
sys.modules.setdefault("PySide6", _pyside)
sys.modules.setdefault("PySide6.QtCore", _qtcore)

sys.path.insert(0, ".")  # 允许在项目根目录直接运行
import timer_logic as tl  # noqa: E402


class TestPomodoroTimer(unittest.TestCase):
    def setUp(self):
        self.t = tl.PomodoroTimer()
        self.t.set_work_minutes(25)
        self.t.set_break_minutes(5)
        self.t.set_long_break_minutes(15)
        self.t.set_long_break_interval(4)

    def test_initial_state(self):
        self.assertEqual(self.t.get_mode(), tl.TimerMode.WORK)
        self.assertEqual(self.t.get_state(), tl.TimerState.IDLE)
        self.assertEqual(self.t.get_remaining_time(), (25, 0))

    def test_long_break_every_n(self):
        results = [self.t.register_work_completed() for _ in range(9)]
        self.assertEqual(results, [False, False, False, True,
                                   False, False, False, True, False])

    def test_duration_by_mode(self):
        self.assertEqual(self.t._duration_seconds(tl.TimerMode.WORK), 25 * 60)
        self.assertEqual(self.t._duration_seconds(tl.TimerMode.BREAK), 5 * 60)
        self.assertEqual(self.t._duration_seconds(tl.TimerMode.LONG_BREAK), 15 * 60)

    def test_no_drift_after_stall(self):
        """模拟系统卡顿：截止时刻已过，tick 后应立即归零（而非按次数递减）。"""
        self.t._paused_remaining = 0.2
        self.t.start()
        time.sleep(0.35)
        self.t.on_timer_tick()
        self.assertEqual(self.t.remaining_seconds, 0)

    def test_pause_resume_keeps_remaining(self):
        self.t._paused_remaining = 10.0
        self.t.start()
        time.sleep(0.15)
        self.t.pause()
        self.assertTrue(9 <= self.t.remaining_seconds <= 10)
        before = self.t.remaining_seconds
        self.t.start()
        self.t.on_timer_tick()
        self.assertTrue(self.t.remaining_seconds <= before)

    def test_reset_restores_duration(self):
        self.t.switch_mode(tl.TimerMode.LONG_BREAK)
        self.t.reset()
        self.assertEqual(self.t.get_remaining_time(), (15, 0))


if __name__ == "__main__":
    unittest.main(verbosity=2)
