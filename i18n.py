# -*- coding: utf-8 -*-
"""轻量多语言模块。

设计目标：
1. 纯 Python，不依赖 Qt，便于在所有平台复用；
2. 以英文原文作为 key，缺省回退英文，新增语言只需补一张字典；
3. 支持“跟随系统”，在设置里可随时切换，切换后无需重启软件。
"""

import locale

LANGUAGES = {
    'system': 'Follow system',
    'zh_CN': '简体中文',
    'en_US': 'English',
    'ja_JP': '日本語',
}

# 字典的 key 统一为英文原文（即默认回退文本）
_TRANSLATIONS = {
    'zh_CN': {
        'Follow system': '跟随系统',
        'Taskbar Pomodoro': '任务栏番茄钟',
        'Settings': '设置',
        'OK': '确定',
        'Cancel': '取消',
        'Timer': '时间设置',
        'Work (minutes):': '工作时长 (分钟):',
        'Short break (minutes):': '短休息时长 (分钟):',
        'Long break (minutes):': '长休息时长 (分钟):',
        'Long break every N pomodoros:': '每几个番茄长休息:',
        'Focus mode': '专注模式',
        'Continuous focus (auto cycle work + break until paused)': '连续专注（工作+休息自动循环，直到手动暂停）',
        'Appearance': '外观主题',
        'Theme:': '界面主题:',
        'Sound': '声音设置',
        'Enable sound': '启用声音提示',
        'Start / next round:': '开始 / 下一轮:',
        'Focus end:': '专注结束:',
        'Options': '选项',
        'Run at startup': '开机自启',
        'Language:': '界面语言:',
        'Classic Deep Space': '经典深空',
        'Light': '清爽浅色',
        'Tomato Red': '番茄红',
        'Forest Green': '森林绿',
        'iOS Modern': 'iOS 现代风',
        'Classic Three-Tones (synth)': '经典三音（合成）',
        'Crisp Bell (synth)': '清脆铃音（合成）',
        'Gentle Duo (synth)': '柔和双音（合成）',
        'Wooden Tap (synth)': '木鱼轻敲（合成）',
        'Digital Beep (synth)': '电子提示（合成）',
        'Morning Sunrise (synth)': '晨光上行（合成）',
        'Complete Chord (synth)': '完成和弦（合成）',
        'Zen Low Tone (synth)': '禅意低音（合成）',
        'Ascending Chime (synth)': '上行提示（合成）',
        'Descending Chime (synth)': '下行提示（合成）',
        'UI Startup (mixkit)': '界面启动（mixkit）',
        'Positive Ping (mixkit)': '积极提示（mixkit）',
        'Marimba (mixkit)': '马林巴琴（mixkit）',
        'Clear Bell (mixkit)': '清亮铃声（mixkit）',
        'Happy Bells (mixkit)': '欢快铃音（mixkit）',
        'Magic Ring (mixkit)': '魔法铃环（mixkit）',
        'Show window': '显示窗口',
        'Hide window': '隐藏窗口',
        '🍅 Focus complete!': '🍅 专注完成！',
        'Nice work! Take a short break before the next round.': '短暂休息一下，准备下一轮专注。',
        'Great job! Take a {minutes}-minute long break.': '已完成一轮，好好休息 {minutes} 分钟吧！',
        'Long break complete!': '长休息结束！',
        'Break complete!': '休息结束！',
        'Ready for the next round!': '准备开始下一轮专注！',
        'Ready to focus!': '准备开始专注！',
        "Today's stats": '今日统计',
        '🍅 Focus today: {minutes} min': '🍅 今日专注：{minutes} 分钟',
        '✅ Pomodoros: {count}': '✅ 完成番茄钟：{count} 次',
        '☕ Break today: {minutes} min': '☕ 今日休息：{minutes} 分钟',
        '📊 Total focus: {minutes} min': '📊 累计专注：{minutes} 分钟',
        'Lock window (disable dragging)': '锁定窗口（禁止拖动）',
        'Locked (dragging disabled) - click to unlock': '已锁定（禁止拖动）——点击解锁',
        'Unlocked (draggable) - click to lock': '已解锁（可拖动位置）——点击锁定',
        '⏸ Pause': '⏸ 暂停',
        '▶ Start': '▶ 开始',
        '↺ Reset': '↺ 重置',
        '🔄 Continuous focus': '🔄 连续专注',
        "📊 Today's stats": '📊 今日统计',
        '⚙ Settings': '⚙ 设置',
        '👁 Hide window': '👁 隐藏窗口',
        '✕ Exit': '✕ 退出',
        'Pomodoro': '番茄钟',
        'Pomodoro {time}': '番茄钟 {time}',
        'Pomodoro - Running': '番茄钟 - 运行中',
        'Running': '运行中',
        'Start': '开始',
        'Pause': '暂停',
        'Reset': '重置',
        'Continuous focus': '连续专注',
        'History': '历史记录',
        'Exit': '退出',
        'Pomodoros completed: <b>{count}</b>': '完成番茄钟: <b>{count}</b> 个',
        'Focus today: <b>{minutes}</b> min': '今日专注: <b>{minutes}</b> 分钟',
        'Total focus: <b>{minutes}</b> min': '累计专注: <b>{minutes}</b> 分钟',
        'Recent records': '最近记录',
        'Time': '时间',
        'Type': '类型',
        'Duration': '时长',
        'Clear records': '清空记录',
        'Close': '关闭',
        'Work': '工作',
        'Break': '休息',
        '{minutes} min': '{minutes} 分钟',
    },
    'en_US': {},  # 英文即 key 本身
    'ja_JP': {
        'Follow system': 'システムに従う',
        'Taskbar Pomodoro': 'タスクバー・ポモドーロ',
        'Settings': '設定',
        'OK': 'OK',
        'Cancel': 'キャンセル',
        'Timer': 'タイマー',
        'Work (minutes):': '作業時間（分）:',
        'Short break (minutes):': '短い休憩（分）:',
        'Long break (minutes):': '長い休憩（分）:',
        'Long break every N pomodoros:': '長い休憩までの回数:',
        'Focus mode': '集中モード',
        'Continuous focus (auto cycle work + break until paused)': '連続集中（作業と休憩を自動で繰り返す）',
        'Appearance': '外観',
        'Theme:': 'テーマ:',
        'Sound': 'サウンド',
        'Enable sound': 'サウンドを有効にする',
        'Start / next round:': '開始 / 次のラウンド:',
        'Focus end:': '集中終了:',
        'Options': 'オプション',
        'Run at startup': '起動時に自動実行',
        'Language:': '言語:',
        'Classic Deep Space': 'クラシックダーク',
        'Light': 'ライト',
        'Tomato Red': 'トマトレッド',
        'Forest Green': 'フォレストグリーン',
        'iOS Modern': 'iOS モダン',
        'Classic Three-Tones (synth)': 'クラシック3音（合成）',
        'Crisp Bell (synth)': 'クリアベル（合成）',
        'Gentle Duo (synth)': 'やわらか2音（合成）',
        'Wooden Tap (synth)': '木魚（合成）',
        'Digital Beep (synth)': 'デジタル音（合成）',
        'Morning Sunrise (synth)': '朝日（合成）',
        'Complete Chord (synth)': '完了和音（合成）',
        'Zen Low Tone (synth)': '禅の低音（合成）',
        'Ascending Chime (synth)': '上昇チャイム（合成）',
        'Descending Chime (synth)': '下降チャイム（合成）',
        'UI Startup (mixkit)': 'UI起動（mixkit）',
        'Positive Ping (mixkit)': 'ポジティブ音（mixkit）',
        'Marimba (mixkit)': 'マリンバ（mixkit）',
        'Clear Bell (mixkit)': 'クリアベル（mixkit）',
        'Happy Bells (mixkit)': 'ハッピーベル（mixkit）',
        'Magic Ring (mixkit)': 'マジックリング（mixkit）',
        'Show window': 'ウィンドウを表示',
        'Hide window': 'ウィンドウを非表示',
        '🍅 Focus complete!': '🍅 集中完了！',
        'Nice work! Take a short break before the next round.': 'よくできました！次のラウンドの前に少し休憩しましょう。',
        'Great job! Take a {minutes}-minute long break.': 'お疲れさま！{minutes}分の長い休憩を取りましょう。',
        'Long break complete!': '長い休憩が終わりました！',
        'Break complete!': '休憩が終わりました！',
        'Ready for the next round!': '次のラウンドを始めましょう！',
        'Ready to focus!': '集中を始めましょう！',
        "Today's stats": '今日の統計',
        '🍅 Focus today: {minutes} min': '🍅 今日の集中: {minutes} 分',
        '✅ Pomodoros: {count}': '✅ 完了したポモドーロ: {count} 回',
        '☕ Break today: {minutes} min': '☕ 今日の休憩: {minutes} 分',
        '📊 Total focus: {minutes} min': '📊 累計集中: {minutes} 分',
        'Lock window (disable dragging)': 'ウィンドウを固定（移動不可）',
        'Locked (dragging disabled) - click to unlock': '固定中（移動不可）- クリックで解除',
        'Unlocked (draggable) - click to lock': '固定解除（移動可）- クリックで固定',
        '⏸ Pause': '⏸ 一時停止',
        '▶ Start': '▶ 開始',
        '↺ Reset': '↺ リセット',
        '🔄 Continuous focus': '🔄 連続集中',
        "📊 Today's stats": '📊 今日の統計',
        '⚙ Settings': '⚙ 設定',
        '👁 Hide window': '👁 ウィンドウを非表示',
        '✕ Exit': '✕ 終了',
        'Pomodoro': 'ポモドーロ',
        'Pomodoro {time}': 'ポモドーロ {time}',
        'Pomodoro - Running': 'ポモドーロ - 実行中',
        'Running': '実行中',
        'Start': '開始',
        'Pause': '一時停止',
        'Reset': 'リセット',
        'Continuous focus': '連続集中',
        'History': '履歴',
        'Exit': '終了',
        'Pomodoros completed: <b>{count}</b>': '完了したポモドーロ: <b>{count}</b> 回',
        'Focus today: <b>{minutes}</b> min': '今日の集中: <b>{minutes}</b> 分',
        'Total focus: <b>{minutes}</b> min': '累計集中: <b>{minutes}</b> 分',
        'Recent records': '最近の記録',
        'Time': '時刻',
        'Type': '種類',
        'Duration': '時間',
        'Clear records': '記録を消去',
        'Close': '閉じる',
        'Work': '作業',
        'Break': '休憩',
        '{minutes} min': '{minutes} 分',
    },
}


def detect_system_language():
    """根据系统区域设置猜测语言，始终返回有效的语言代码。"""
    try:
        code = (locale.getdefaultlocale()[0] or '').lower()
    except Exception:
        code = ''
    if code.startswith('zh'):
        return 'zh_CN'
    if code.startswith('ja'):
        return 'ja_JP'
    return 'en_US'


class I18n:
    def __init__(self):
        self.language = 'system'
        self.active = 'en_US'

    def set_language(self, code):
        """设置界面语言。code 可为 system / zh_CN / en_US / ja_JP。"""
        self.language = code if code in LANGUAGES else 'system'
        self.active = (detect_system_language()
                       if self.language == 'system' else self.language)
        if self.active not in _TRANSLATIONS:
            self.active = 'en_US'

    def tr(self, text, **kwargs):
        translated = _TRANSLATIONS.get(self.active, {}).get(text, text)
        return translated.format(**kwargs) if kwargs else translated

    def language_name(self, code):
        return self.tr(LANGUAGES.get(code, code))


i18n = I18n()


def tr(text, **kwargs):
    return i18n.tr(text, **kwargs)


def language_items():
    """返回设置下拉框用的 (显示名, code) 列表。"""
    return [(i18n.language_name(code), code) for code in LANGUAGES]
