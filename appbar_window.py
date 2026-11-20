import ctypes
from ctypes import wintypes

from PySide6.QtWidgets import (
    QWidget, QLabel, QPushButton, QComboBox,
    QHBoxLayout, QSpacerItem, QSizePolicy, QMenu
)
from PySide6.QtCore import Qt, QTimer, QPoint, Signal
from PySide6.QtGui import (
    QFont, QColor, QPainter, QPen, QBrush, QLinearGradient,
    QGuiApplication, QAction
)

user32 = ctypes.windll.user32
shell32 = ctypes.windll.shell32

# ── Windows API constants ──────────────────────────────────────────
SWP_NOMOVE = 0x0002
SWP_NOSIZE = 0x0001
SWP_NOACTIVATE = 0x0010
SWP_SHOWWINDOW = 0x0040
SWP_FRAMECHANGED = 0x0020

GWL_EXSTYLE = -20
WS_EX_TOPMOST = 0x00000008
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_NOACTIVATE = 0x08000000
WS_EX_LAYERED = 0x00080000

HWND_TOPMOST = -1
HWND_NOTOPMOST = -2


class RECT(ctypes.Structure):
    _fields_ = [
        ("left", wintypes.LONG),
        ("top", wintypes.LONG),
        ("right", wintypes.LONG),
        ("bottom", wintypes.LONG),
    ]


# ── 64位兼容：设置函数签名 ──────────────────────────────────────
user32.SetWindowPos.restype = wintypes.BOOL
user32.SetWindowPos.argtypes = [
    wintypes.HWND, wintypes.HWND,
    ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
    wintypes.UINT
]
user32.GetWindowLongW.restype = wintypes.LONG
user32.GetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int]
user32.SetWindowLongW.restype = wintypes.LONG
user32.SetWindowLongW.argtypes = [wintypes.HWND, ctypes.c_int, wintypes.LONG]
user32.FindWindowW.restype = wintypes.HWND
user32.FindWindowW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR]
user32.GetWindowRect.restype = wintypes.BOOL
user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(RECT)]
user32.BringWindowToTop.restype = wintypes.BOOL
user32.BringWindowToTop.argtypes = [wintypes.HWND]
user32.GetForegroundWindow.restype = wintypes.HWND
user32.GetForegroundWindow.argtypes = []


class _TopmostComboBox(QComboBox):
    """预设下拉：弹出层置顶，并在打开期间暂停宿主窗口的 topmost 刷新。"""

    def __init__(self, host, parent=None):
        super().__init__(parent)
        self._host = host

    def showPopup(self):
        host = self._host
        if host is not None and host.topmost_timer.isActive():
            host.topmost_timer.stop()
        super().showPopup()
        # 不改 windowFlags（会重建弹出层）；仅 Win32 TOPMOST 压过宿主覆盖窗
        try:
            popup = self.view().window()
            if popup is not None:
                hwnd = int(popup.winId())
                if hwnd:
                    user32.SetWindowPos(
                        hwnd, HWND_TOPMOST, 0, 0, 0, 0,
                        SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_SHOWWINDOW
                    )
                    user32.BringWindowToTop(hwnd)
        except Exception:
            pass

    def hidePopup(self):
        super().hidePopup()
        host = self._host
        if host is not None:
            host._resume_topmost_if_needed()


class PomodoroWindow(QWidget):
    start_pause_clicked = Signal()
    reset_clicked = Signal()
    preset_changed = Signal(str)
    pin_toggled = Signal(bool)
    settings_requested = Signal()
    stats_requested = Signal()
    continuous_focus_toggled = Signal(bool)
    hide_requested = Signal()
    exit_requested = Signal()

    def __init__(self, settings_manager):
        super().__init__()
        self.settings_manager = settings_manager
        self.dragging = False
        self.drag_start_pos = QPoint()
        self.is_pinned = True
        self.progress = 0.0
        self.is_work_mode = True

        self.topmost_timer = QTimer(self)
        self.topmost_timer.setInterval(50)
        self.topmost_timer.timeout.connect(self.on_topmost_timeout)

        self.init_ui()
        self.load_position()

    def init_ui(self):
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 扁平化样式（逻辑像素，Qt6 自动处理 DPI 缩放）
        self.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 6px;
                color: rgba(255, 255, 255, 0.82);
                font-size: 20px;
                padding: 0px;
            }
            QPushButton:hover {
                color: rgba(255, 255, 255, 1.0);
                background: rgba(255, 255, 255, 0.08);
            }
            QPushButton:pressed {
                background: rgba(255, 255, 255, 0.16);
            }
            QComboBox {
                background: rgba(255, 255, 255, 0.06);
                border: none;
                border-radius: 5px;
                color: rgba(255, 255, 255, 0.88);
                font-size: 12px;
                padding: 3px 6px;
                min-width: 46px;
                max-width: 56px;
            }
            QComboBox::drop-down {
                border: none;
                width: 16px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 3px solid transparent;
                border-right: 3px solid transparent;
                border-top: 4px solid rgba(255, 255, 255, 0.6);
                margin-right: 4px;
            }
            QComboBox QAbstractItemView {
                background-color: #1a1a28;
                color: #e0e0e8;
                selection-background-color: #2e2e44;
                border: 1px solid #2a2a3c;
                border-radius: 6px;
                outline: none;
                padding: 4px;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 2, 10, 2)
        layout.setSpacing(8)

        # 圆环
        self.progress_widget = ProgressRing()
        layout.addWidget(self.progress_widget)

        # 时间标签
        self.time_label = QLabel("25:00")
        self.time_label.setStyleSheet("color: rgba(255, 255, 255, 0.95);")
        self.time_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.time_label)

        layout.addSpacerItem(QSpacerItem(6, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # 预设：使用子类保证弹出层在主窗口（HWND_TOPMOST）之上
        self.preset_combo = _TopmostComboBox(self)
        self.preset_combo.addItems(["5/1", "15/5", "25/5", "30/5"])
        self.preset_combo.currentTextChanged.connect(self.on_preset_changed)
        layout.addWidget(self.preset_combo)

        # 按钮
        self.start_btn = QPushButton("▶")
        self.start_btn.clicked.connect(self.on_start_pause)
        layout.addWidget(self.start_btn)

        self.reset_btn = QPushButton("↺")
        self.reset_btn.clicked.connect(self.on_reset)
        layout.addWidget(self.reset_btn)

        self.pin_btn = QPushButton("📍")
        self.pin_btn.setToolTip("锁定窗口（禁止拖动）")
        self.pin_btn.clicked.connect(self.on_pin_toggle)
        layout.addWidget(self.pin_btn)

        # 根据当前屏幕计算尺寸
        self._apply_sizing()

    def _apply_sizing(self):
        """根据当前屏幕的任务栏高度，用逻辑像素设置窗口和控件尺寸"""
        taskbar_h = self._get_taskbar_height_logical()
        self._win_h = max(36, taskbar_h)
        self.setFixedHeight(self._win_h)
        self.setMinimumWidth(260)

        content_h = self._win_h - 4  # 上下各 2px margin

        # 圆环
        ring_size = min(44, content_h)
        self.progress_widget.setFixedSize(ring_size, ring_size)

        # 时间标签
        font_size = max(11, int(self._win_h * 0.36))
        self.time_label.setFont(QFont("Segoe UI", font_size, QFont.Bold))

        # 按钮
        btn_size = min(40, content_h)
        for btn in (self.start_btn, self.reset_btn, self.pin_btn):
            btn.setFixedSize(btn_size, btn_size)

        self.adjustSize()

    def _get_taskbar_height_logical(self):
        """用 Qt 屏幕几何信息获取任务栏高度（逻辑像素，自动适配 DPI）"""
        screen = self.screen() or QGuiApplication.primaryScreen()
        if screen:
            return screen.geometry().height() - screen.availableGeometry().height()
        return 40

    def _on_screen_changed(self):
        """窗口移动到不同分辨率/DPI 屏幕时重新计算尺寸"""
        self._apply_sizing()

    def _resume_topmost_if_needed(self):
        if self.isVisible() and not self.topmost_timer.isActive():
            self.topmost_timer.start()

    # ── Windows topmost ────────────────────────────────────────────
    def _apply_windows_topmost_style(self):
        hwnd = int(self.winId())
        if not hwnd:
            return
        try:
            current_style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            new_style = current_style | WS_EX_TOPMOST | WS_EX_NOACTIVATE
            user32.SetWindowLongW(hwnd, GWL_EXSTYLE, new_style)
            user32.SetWindowPos(
                hwnd, 0, 0, 0, 0, 0,
                SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_FRAMECHANGED
            )
        except Exception:
            pass

    def showEvent(self, event):
        super().showEvent(event)
        self._apply_windows_topmost_style()
        self.set_window_topmost(True)
        # 监听屏幕切换（跨屏幕拖动时自动重算 DPI 尺寸；只连接一次）
        wh = self.windowHandle()
        if wh and not getattr(self, '_screen_changed_connected', False):
            wh.screenChanged.connect(self._on_screen_changed)
            self._screen_changed_connected = True

    def set_window_topmost(self, topmost):
        hwnd = int(self.winId())
        if not hwnd:
            return
        if topmost:
            user32.SetWindowPos(
                hwnd, HWND_TOPMOST, 0, 0, 0, 0,
                SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_SHOWWINDOW
            )
            user32.BringWindowToTop(hwnd)
            if not self.topmost_timer.isActive():
                self.topmost_timer.start()
        else:
            user32.SetWindowPos(
                hwnd, HWND_NOTOPMOST, 0, 0, 0, 0,
                SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE
            )
            if self.topmost_timer.isActive():
                self.topmost_timer.stop()

    def on_topmost_timeout(self):
        if self.isVisible():
            hwnd = int(self.winId())
            if hwnd:
                user32.SetWindowPos(
                    hwnd, HWND_TOPMOST, 0, 0, 0, 0,
                    SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_SHOWWINDOW
                )
                user32.BringWindowToTop(hwnd)

    # ── 绘制（精致半透明背景）──────────────────────────────────────
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect()

        # 主背景渐变
        gradient = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        if self.is_work_mode:
            gradient.setColorAt(0, QColor(26, 26, 36, 175))
            gradient.setColorAt(1, QColor(20, 20, 30, 185))
        else:
            gradient.setColorAt(0, QColor(20, 36, 28, 175))
            gradient.setColorAt(1, QColor(16, 30, 24, 185))

        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect, 8, 8)

        # 顶部高光（玻璃质感）
        highlight_rect = rect.adjusted(1, 1, -1, -rect.height() // 2)
        highlight = QLinearGradient(highlight_rect.topLeft(), highlight_rect.bottomLeft())
        highlight.setColorAt(0, QColor(255, 255, 255, 18))
        highlight.setColorAt(1, QColor(255, 255, 255, 0))
        painter.setBrush(QBrush(highlight))
        painter.drawRoundedRect(rect, 8, 8)

        # 细边框
        border_pen = QPen(QColor(255, 255, 255, 12), 1)
        painter.setPen(border_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(rect.adjusted(0, 0, -1, -1), 8, 8)

    # ── 右键菜单 ──────────────────────────────────────────────────
    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1a1a28;
                color: #e0e0e8;
                border: 1px solid #2e2e44;
                border-radius: 8px;
                padding: 6px;
            }
            QMenu::item {
                padding: 6px 28px;
                border-radius: 4px;
                font-size: 13px;
            }
            QMenu::item:selected {
                background-color: #2e2e44;
            }
            QMenu::separator {
                height: 1px;
                background-color: #2e2e44;
                margin: 4px 10px;
            }
            QMenu::indicator {
                width: 16px;
            }
        """)

        is_running = (self.start_btn.text() == "⏸")
        toggle_action = QAction("⏸ 暂停" if is_running else "▶ 开始", menu)
        toggle_action.triggered.connect(self.on_start_pause)
        menu.addAction(toggle_action)

        reset_action = QAction("↺ 重置", menu)
        reset_action.triggered.connect(self.on_reset)
        menu.addAction(reset_action)

        menu.addSeparator()

        continuous_action = QAction("🔄 连续专注", menu)
        continuous_action.setCheckable(True)
        continuous_action.setChecked(self.settings_manager.get('continuous_focus'))
        continuous_action.toggled.connect(self.continuous_focus_toggled.emit)
        menu.addAction(continuous_action)

        menu.addSeparator()

        stats_action = QAction("📊 今日统计", menu)
        stats_action.triggered.connect(self.stats_requested.emit)
        menu.addAction(stats_action)

        settings_action = QAction("⚙ 设置", menu)
        settings_action.triggered.connect(self.settings_requested.emit)
        menu.addAction(settings_action)

        menu.addSeparator()

        hide_action = QAction("👁 隐藏窗口", menu)
        hide_action.triggered.connect(self.hide_requested.emit)
        menu.addAction(hide_action)

        exit_action = QAction("✕ 退出", menu)
        exit_action.triggered.connect(self.exit_requested.emit)
        menu.addAction(exit_action)

        menu.exec(event.globalPos())

    # ── 鼠标拖动 ──────────────────────────────────────────────────
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and not self.is_pinned:
            self.dragging = True
            self.drag_start_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.dragging and not self.is_pinned:
            new_pos = event.globalPosition().toPoint() - self.drag_start_pos
            virtual_geo = QGuiApplication.primaryScreen().virtualGeometry()
            new_pos.setX(max(virtual_geo.left(), min(new_pos.x(), virtual_geo.right() - self.width())))
            new_pos.setY(max(virtual_geo.top(), min(new_pos.y(), virtual_geo.bottom() - self.height())))
            self.move(new_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.dragging:
            self.dragging = False
            self.save_position()
            event.accept()

    # ── 定位 ──────────────────────────────────────────────────────
    def position_on_taskbar(self):
        """默认定位：从右到左 1/4 处，底部覆盖任务栏"""
        screen_geo = self.screen().geometry()
        x = int(screen_geo.width() * 3 / 4) - self.width() // 2
        y = screen_geo.height() - self.height()
        self.move(x, max(0, y))
        self.save_position()

    def load_position(self):
        x = self.settings_manager.get('window_x')
        y = self.settings_manager.get('window_y')
        if x is not None and y is not None:
            self.move(x, y)
        else:
            self.position_on_taskbar()

    def save_position(self):
        pos = self.pos()
        self.settings_manager.set('window_x', pos.x())
        self.settings_manager.set('window_y', pos.y())

    # ── 按钮事件 ──────────────────────────────────────────────────
    def on_start_pause(self):
        self.start_pause_clicked.emit()

    def on_reset(self):
        self.reset_clicked.emit()

    def on_preset_changed(self, text):
        self.preset_changed.emit(text)

    def on_pin_toggle(self):
        self.is_pinned = not self.is_pinned
        if self.is_pinned:
            self.dragging = False
            self.pin_btn.setText("📍")
            self.pin_btn.setToolTip("已锁定（禁止拖动）——点击解锁")
            self.save_position()
        else:
            self.pin_btn.setText("🔓")
            self.pin_btn.setToolTip("已解锁（可拖动位置）——点击锁定")
        self.pin_toggled.emit(self.is_pinned)

    # ── 外部调用接口 ──────────────────────────────────────────────
    def update_time_display(self, minutes, seconds):
        self.time_label.setText(f"{minutes:02d}:{seconds:02d}")

    def update_progress(self, current, total):
        if total > 0:
            self.progress = current / total
            self.progress_widget.update_progress(self.progress, self.is_work_mode)

    def set_running_state(self, is_running):
        self.start_btn.setText("⏸" if is_running else "▶")

    def set_mode(self, is_work_mode):
        self.is_work_mode = is_work_mode
        self.progress_widget.set_mode(is_work_mode)
        self.update()

    def set_pinned(self, pinned):
        self.is_pinned = pinned
        if pinned:
            self.pin_btn.setText("📍")
            self.pin_btn.setToolTip("已锁定（禁止拖动）——点击解锁")
        else:
            self.pin_btn.setText("🔓")
            self.pin_btn.setToolTip("已解锁（可拖动位置）——点击锁定")

    def update_preset_from_settings(self, work, break_min):
        """同步预设下拉框，不触发信号"""
        text = f"{work}/{break_min}"
        self.preset_combo.blockSignals(True)
        idx = self.preset_combo.findText(text)
        if idx >= 0:
            self.preset_combo.setCurrentIndex(idx)
        self.preset_combo.blockSignals(False)


class ProgressRing(QWidget):
    def __init__(self):
        super().__init__()
        self.progress = 0.0
        self.is_work_mode = True

    def update_progress(self, progress, is_work_mode):
        self.progress = progress
        self.is_work_mode = is_work_mode
        self.update()

    def set_mode(self, is_work_mode):
        self.is_work_mode = is_work_mode
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()
        center = rect.center()

        # 根据控件大小自适应线宽（留足 RoundCap 的扩展空间）
        side = min(rect.width(), rect.height())
        pen_width = max(3, side // 8)
        # radius 缩小更多，确保 RoundCap 不超出控件边界
        radius = side // 2 - pen_width - 1
        inner_radius = max(2, radius - pen_width - 2)

        # 背景圆环
        bg_pen = QPen(QColor(255, 255, 255, 35), pen_width)
        painter.setPen(bg_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(center, radius, radius)

        # 进度圆环：工作=暖红渐变，休息=翠绿渐变
        if self.is_work_mode:
            color1 = QColor(255, 95, 75)
            color2 = QColor(255, 160, 110)
        else:
            color1 = QColor(70, 210, 150)
            color2 = QColor(120, 230, 180)

        gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
        gradient.setColorAt(0, color1)
        gradient.setColorAt(1, color2)

        progress_pen = QPen(gradient, pen_width)
        progress_pen.setCapStyle(Qt.RoundCap)
        painter.setPen(progress_pen)

        start_angle = 90 * 16
        span_angle = -int(self.progress * 360 * 16)
        painter.drawArc(
            center.x() - radius,
            center.y() - radius,
            radius * 2,
            radius * 2,
            start_angle,
            span_angle
        )

        # 内圈装饰
        inner_gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
        if self.is_work_mode:
            inner_gradient.setColorAt(0, QColor(255, 95, 75, 22))
            inner_gradient.setColorAt(1, QColor(255, 160, 110, 35))
        else:
            inner_gradient.setColorAt(0, QColor(70, 210, 150, 22))
            inner_gradient.setColorAt(1, QColor(120, 230, 180, 35))

        painter.setBrush(QBrush(inner_gradient))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center, inner_radius, inner_radius)
