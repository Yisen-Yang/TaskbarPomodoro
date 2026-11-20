"""音效注册表：把所有可选提示音集中管理。

每项: (key, 显示名, 文件名, 类别)
类别: 'start' 开始 / 'end' 结束 / 'both' 通用
文件名按优先级查找 .wav（MCI waveaudio）/ .mp3（MCI mpegvideo）。
"""

SOUNDS = [
    # 代码合成（零版权，体积小）
    ("classic",       "经典三音（合成）",   "s_classic.wav",   "both"),
    ("chime",        "清脆铃音（合成）",   "s_chime.wav",     "end"),
    ("gentle",       "柔和双音（合成）",   "s_gentle.wav",    "both"),
    ("wood",         "木鱼轻敲（合成）",   "s_wood.wav",      "start"),
    ("digital",      "电子提示（合成）",   "s_digital.wav",   "start"),
    ("sunrise",      "晨光上行（合成）",   "s_sunrise.wav",   "start"),
    ("complete",     "完成和弦（合成）",   "s_complete.wav",  "end"),
    ("zen",          "禅意低音（合成）",   "s_zen.wav",       "end"),
    # mixkit 免费音效（个人/商业可用，不可单独转售音频文件本身）
    ("mix_software", "界面启动（mixkit）", "mix_start_software.mp3",  "start"),
    ("mix_positive", "积极提示（mixkit）", "mix_start_positive.mp3",  "start"),
    ("mix_marimba",  "马林巴琴（mixkit）", "mix_start_marimba.mp3",   "start"),
    ("mix_bell",     "清亮铃声（mixkit）", "mix_end_bell.mp3",        "end"),
    ("mix_happy",    "欢快铃音（mixkit）", "mix_end_happybells.mp3",  "end"),
    ("mix_ring",     "魔法铃环（mixkit）", "mix_end_magicring.mp3",   "end"),
]

BY_KEY = {k: (k, label, filename, cat) for k, label, filename, cat in SOUNDS}


def display_names(category=None):
    """返回 (显示名, key) 列表，可按类别过滤。"""
    out = []
    for key, label, filename, cat in SOUNDS:
        if category is None or cat in (category, 'both'):
            out.append((label, key))
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
    return item[1] if item else "经典三音（合成）"
