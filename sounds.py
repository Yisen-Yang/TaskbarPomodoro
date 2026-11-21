"""音效注册表：把所有可选提示音集中管理。

每项: (key, 显示名英文原文, 文件名, 类别)
类别: 'start' 开始 / 'end' 结束 / 'both' 通用
文件名按优先级查找 .wav（MCI waveaudio）/ .mp3（MCI mpegvideo）。
显示名统一通过 i18n 翻译，键即英文原文。
"""

from i18n import tr

SOUNDS = [
    # 代码合成（零版权，体积小）
    ("classic",      "Classic Three-Tones (synth)",  "s_classic.wav",   "both"),
    ("chime",        "Crisp Bell (synth)",           "s_chime.wav",     "end"),
    ("gentle",       "Gentle Duo (synth)",           "s_gentle.wav",    "both"),
    ("wood",         "Wooden Tap (synth)",           "s_wood.wav",      "start"),
    ("digital",      "Digital Beep (synth)",         "s_digital.wav",   "start"),
    ("sunrise",      "Morning Sunrise (synth)",      "s_sunrise.wav",   "start"),
    ("complete",     "Complete Chord (synth)",       "s_complete.wav",  "end"),
    ("zen",          "Zen Low Tone (synth)",         "s_zen.wav",       "end"),
    # 新增：方向明确的一对默认音（上行 / 下行）
    ("start_up",     "Ascending Chime (synth)",      "s_start_up.wav",   "start"),
    ("end_down",     "Descending Chime (synth)",     "s_end_down.wav",   "end"),
    # mixkit 免费音效
    ("mix_software", "UI Startup (mixkit)",          "mix_start_software.mp3",  "start"),
    ("mix_positive", "Positive Ping (mixkit)",       "mix_start_positive.mp3",  "start"),
    ("mix_marimba",  "Marimba (mixkit)",             "mix_start_marimba.mp3",   "start"),
    ("mix_bell",     "Clear Bell (mixkit)",          "mix_end_bell.mp3",        "end"),
    ("mix_happy",    "Happy Bells (mixkit)",         "mix_end_happybells.mp3",  "end"),
    ("mix_ring",     "Magic Ring (mixkit)",          "mix_end_magicring.mp3",   "end"),
]

BY_KEY = {k: (k, label, filename, cat) for k, label, filename, cat in SOUNDS}


def display_names(category=None):
    """返回 (显示名, key) 列表，可按类别过滤。"""
    out = []
    for key, label, filename, cat in SOUNDS:
        if category is None or cat in (category, 'both'):
            out.append((tr(label), key))
    return out


def resolve(key):
    """根据 key 返回 (文件名, MCI 类型)；未知 key 回退到 classic。"""
    item = BY_KEY.get(key) or BY_KEY['classic']
    filename = item[2]
    if filename.lower().endswith('.wav'):
        return filename, 'waveaudio'
    return filename, 'mpegvideo'


def label_of(key):
    item = BY_KEY.get(key)
    return tr(item[1]) if item else tr('Classic Three-Tones (synth)')
