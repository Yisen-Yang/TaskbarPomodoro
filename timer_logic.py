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

class PomodoroTimer(QObject):
    time_updated = Signal(int, int)
    state_changed = Signal(TimerState)
    mode_changed = Signal(TimerMode)
    timer_completed = Signal(TimerMode)
    
    def __init__(self):
        super().__init__()
        self.work_minutes = 25
        self.break_minutes = 5
        self.current_mode = TimerMode.WORK
        self.current_state = TimerState.IDLE
        self.remaining_seconds = self.work_minutes * 60
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.on_timer_tick)
    
    def set_work_minutes(self, minutes):
        self.work_minutes = minutes
        if self.current_state == TimerState.IDLE and self.current_mode == TimerMode.WORK:
            self.remaining_seconds = minutes * 60
            self.notify_time_update()
    
    def set_break_minutes(self, minutes):
        self.break_minutes = minutes
        if self.current_state == TimerState.IDLE and self.current_mode == TimerMode.BREAK:
            self.remaining_seconds = minutes * 60
            self.notify_time_update()
    
    def start(self):
        if self.current_state == TimerState.COMPLETED:
            self.reset()
        
        self.current_state = TimerState.RUNNING
        self.state_changed.emit(self.current_state)
        self.timer.start()
    
    def pause(self):
        if self.current_state == TimerState.RUNNING:
            self.current_state = TimerState.PAUSED
            self.state_changed.emit(self.current_state)
            self.timer.stop()
    
    def reset(self):
        self.timer.stop()
        self.current_state = TimerState.IDLE
        
        if self.current_mode == TimerMode.WORK:
            self.remaining_seconds = self.work_minutes * 60
        else:
            self.remaining_seconds = self.break_minutes * 60
        
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
        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            self.notify_time_update()
        else:
            self.complete()
    
    def complete(self):
        self.timer.stop()
        self.current_state = TimerState.COMPLETED
        self.state_changed.emit(self.current_state)
        self.timer_completed.emit(self.current_mode)
    
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
