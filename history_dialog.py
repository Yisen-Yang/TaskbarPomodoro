from datetime import datetime, date, timedelta

from PySide6.QtWidgets import (
    QDialog, QLabel, QTableWidget, QTableWidgetItem, QWidget,
    QPushButton, QVBoxLayout, QHBoxLayout, QGroupBox,
    QHeaderView
)
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import (
    QColor, QPainter, QPen, QBrush, QLinearGradient, QPalette
)
from app_icon import get_app_icon
from i18n import tr



class TrendBar(QWidget):
    """趋势图里的单根柱子：圆角渐变 + 顶部数值 + 底部星期。"""

    def __init__(self, value, maximum, label, parent=None):
        super().__init__(parent)
        self.value = value
        self.maximum = max(1, maximum)
        self.day_label = label
        self.setFixedHeight(104)
        self.setMinimumWidth(28)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        text_color = self.palette().color(QPalette.WindowText)

        bar_h = max(3, int((h - 26) * min(1.0, self.value / self.maximum)))
        rect = QRect(5, h - 24 - bar_h, w - 10, bar_h)
        gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
        gradient.setColorAt(0, QColor('#ff6b5a'))
        gradient.setColorAt(1, QColor('#ffa06e'))
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect, 4, 4)

        painter.setPen(QPen(text_color))
        if self.value:
            painter.drawText(QRect(0, rect.top() - 15, w, 14),
                             Qt.AlignCenter, str(self.value))
        painter.drawText(QRect(0, h - 20, w, 16),
                         Qt.AlignCenter, self.day_label)


class HistoryDialog(QDialog):
    def __init__(self, history_manager, parent=None):
        super().__init__(parent)
        self.history_manager = history_manager
        self.setWindowTitle(tr("History"))
        self.setWindowIcon(get_app_icon())
        self.setFixedSize(560, 520)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        stats_group = QGroupBox(tr("Today's stats"))
        stats_layout = QHBoxLayout(stats_group)
        stats_layout.setSpacing(20)

        today_pomodoros = self.history_manager.get_today_pomodoros()
        today_work_minutes = self.history_manager.get_today_work_minutes()
        total_work_minutes = self.history_manager.get_total_work_minutes()

        pomodoro_label = QLabel(
            tr("Pomodoros completed: <b>{count}</b>", count=today_pomodoros))
        pomodoro_label.setStyleSheet("font-size: 14px;")
        stats_layout.addWidget(pomodoro_label)

        today_work_label = QLabel(
            tr("Focus today: <b>{minutes}</b> min", minutes=today_work_minutes))
        today_work_label.setStyleSheet("font-size: 14px;")
        stats_layout.addWidget(today_work_label)

        total_work_label = QLabel(
            tr("Total focus: <b>{minutes}</b> min", minutes=total_work_minutes))
        total_work_label.setStyleSheet("font-size: 14px;")
        stats_layout.addWidget(total_work_label)

        layout.addWidget(stats_group)

        # ── 近 7 日趋势（复用已有数据层）──
        weekly = self.history_manager.get_weekly_stats()
        trend_group = QGroupBox(tr("Last 7 days · focus minutes"))
        trend_layout = QHBoxLayout(trend_group)
        trend_layout.setContentsMargins(10, 8, 10, 8)
        trend_layout.setSpacing(6)
        today = date.today()
        values = []
        for offset in range(6, -1, -1):
            day = today - timedelta(days=offset)
            minutes = weekly.get(day.isoformat(), {}).get('work', 0)
            values.append((minutes, day.strftime('%a')[:2]))
        maximum = max([v for v, _ in values] + [25])
        for minutes, label in values:
            trend_layout.addWidget(TrendBar(minutes, maximum, label))
        layout.addWidget(trend_group)

        table_group = QGroupBox(tr("Recent records"))
        table_layout = QVBoxLayout(table_group)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels([tr("Time"), tr("Type"), tr("Duration")])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionMode(QTableWidget.NoSelection)

        self.load_records()

        table_layout.addWidget(self.table)
        layout.addWidget(table_group)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        clear_btn = QPushButton(tr("Clear records"))
        clear_btn.clicked.connect(self.on_clear)
        btn_layout.addWidget(clear_btn)

        close_btn = QPushButton(tr("Close"))
        close_btn.clicked.connect(self.close)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)

    def load_records(self):
        records = self.history_manager.get_recent_records(20)
        self.table.setRowCount(len(records))

        for row, record in enumerate(records):
            try:
                dt = datetime.fromisoformat(record['completed_at'])
                time_str = dt.strftime('%m-%d %H:%M')
            except (ValueError, KeyError, TypeError):
                time_str = record.get('completed_at', '')[:16] if isinstance(record, dict) else ''

            if not isinstance(record, dict):
                continue
            mode_str = tr("Work") if record.get('mode') == 'work' else tr("Break")
            mode_color = (QColor("#ff6450") if record.get('mode') == 'work'
                          else QColor("#50c896"))

            duration_str = tr("{minutes} min", minutes=record.get('duration_minutes', 0))

            time_item = QTableWidgetItem(time_str)
            time_item.setTextAlignment(Qt.AlignCenter)

            mode_item = QTableWidgetItem(mode_str)
            mode_item.setTextAlignment(Qt.AlignCenter)
            mode_item.setForeground(mode_color)

            duration_item = QTableWidgetItem(duration_str)
            duration_item.setTextAlignment(Qt.AlignCenter)

            self.table.setItem(row, 0, time_item)
            self.table.setItem(row, 1, mode_item)
            self.table.setItem(row, 2, duration_item)

    def on_clear(self):
        self.history_manager.clear_history()
        self.load_records()
