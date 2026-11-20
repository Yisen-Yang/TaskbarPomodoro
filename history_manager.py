import os
import json
from datetime import datetime, timedelta
from collections import defaultdict

class HistoryManager:
    def __init__(self):
        self.records = []
        self.load_history()
    
    def get_history_path(self):
        app_data = os.environ.get('APPDATA', os.path.expanduser('~'))
        return os.path.join(app_data, 'PomodoroTaskbar', 'history.json')
    
    def load_history(self):
        try:
            history_path = self.get_history_path()
            if os.path.exists(history_path):
                with open(history_path, 'r', encoding='utf-8') as f:
                    self.records = json.load(f)
        except Exception:
            self.records = []
    
    def save_history(self):
        try:
            history_path = self.get_history_path()
            os.makedirs(os.path.dirname(history_path), exist_ok=True)
            with open(history_path, 'w', encoding='utf-8') as f:
                json.dump(self.records, f, indent=2, ensure_ascii=False)
        except Exception:
            pass
    
    def add_record(self, mode, duration_minutes, completed_at=None):
        if completed_at is None:
            completed_at = datetime.now().isoformat()
        
        record = {
            'mode': mode,
            'duration_minutes': duration_minutes,
            'completed_at': completed_at
        }
        self.records.append(record)
        self.save_history()
    
    def get_today_records(self):
        today = datetime.now().strftime('%Y-%m-%d')
        return [r for r in self.records if r['completed_at'].startswith(today)]
    
    def get_week_records(self):
        now = datetime.now()
        week_ago = now - timedelta(days=7)
        return [r for r in self.records if datetime.fromisoformat(r['completed_at']) >= week_ago]
    
    def get_total_work_minutes(self):
        return sum(r['duration_minutes'] for r in self.records if r['mode'] == 'work')
    
    def get_today_work_minutes(self):
        records = self.get_today_records()
        return sum(r['duration_minutes'] for r in records if r['mode'] == 'work')
    
    def get_today_pomodoros(self):
        records = self.get_today_records()
        return sum(1 for r in records if r['mode'] == 'work')

    def get_today_break_minutes(self):
        records = self.get_today_records()
        return sum(r['duration_minutes'] for r in records if r['mode'] == 'break')
    
    def get_weekly_stats(self):
        records = self.get_week_records()
        daily_stats = defaultdict(lambda: {'work': 0, 'break': 0, 'count': 0})
        
        for record in records:
            date = record['completed_at'][:10]
            if record['mode'] == 'work':
                daily_stats[date]['work'] += record['duration_minutes']
                daily_stats[date]['count'] += 1
            else:
                daily_stats[date]['break'] += record['duration_minutes']
        
        return dict(daily_stats)
    
    def clear_history(self):
        self.records = []
        self.save_history()
    
    def get_recent_records(self, limit=20):
        return sorted(self.records, key=lambda r: r['completed_at'], reverse=True)[:limit]
