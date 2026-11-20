from datetime import datetime

from PySide6.QtWidgets import (
    QDialog, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QVBoxLayout, QHBoxLayout, QGroupBox,
    QHeaderView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from app_icon import get_app_icon


class HistoryDialog(QDialog):
    def __init__(self, history_manager, parent=None):
        super().__init__(parent)
        self.history_manager = history_manager
        self.setWindowTitle("历史记录")
        self.setWindowIcon(get_app_icon())
        self.setFixedSize(500, 400)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        
        stats_group = QGroupBox("今日统计")
        stats_layout = QHBoxLayout(stats_group)
        stats_layout.setSpacing(20)
        
        today_pomodoros = self.history_manager.get_today_pomodoros()
        today_work_minutes = self.history_manager.get_today_work_minutes()
        total_work_minutes = self.history_manager.get_total_work_minutes()
        
        pomodoro_label = QLabel(f"完成番茄钟: <b>{today_pomodoros}</b> 个")
        pomodoro_label.setStyleSheet("font-size: 14px;")
        stats_layout.addWidget(pomodoro_label)
        
        today_work_label = QLabel(f"今日专注: <b>{today_work_minutes}</b> 分钟")
        today_work_label.setStyleSheet("font-size: 14px;")
        stats_layout.addWidget(today_work_label)
        
        total_work_label = QLabel(f"累计专注: <b>{total_work_minutes}</b> 分钟")
        total_work_label.setStyleSheet("font-size: 14px;")
        stats_layout.addWidget(total_work_label)
        
        layout.addWidget(stats_group)
        
        table_group = QGroupBox("最近记录")
        table_layout = QVBoxLayout(table_group)
        
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["时间", "类型", "时长"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionMode(QTableWidget.NoSelection)
        
        self.load_records()
        
        table_layout.addWidget(self.table)
        layout.addWidget(table_group)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        clear_btn = QPushButton("清空记录")
        clear_btn.clicked.connect(self.on_clear)
        btn_layout.addWidget(clear_btn)
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.close)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
    
    def load_records(self):
        records = self.history_manager.get_recent_records(20)
        self.table.setRowCount(len(records))
        
        for row, record in enumerate(records):
            dt = datetime.fromisoformat(record['completed_at'])
            time_str = dt.strftime('%m-%d %H:%M')
            
            mode_str = "工作" if record['mode'] == 'work' else "休息"
            mode_color = QColor("#ff6450") if record['mode'] == 'work' else QColor("#50c896")
            
            duration_str = f"{record['duration_minutes']} 分钟"
            
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
