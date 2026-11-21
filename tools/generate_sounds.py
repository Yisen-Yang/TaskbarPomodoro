# -*- coding: utf-8 -*-
"""生成一对方向明确的默认提示音：上行（开始）/ 下行（结束）。

只依赖标准库，生成 44.1kHz / 16bit / 单声道 WAV，可直接被系统播放器播放。
"""

import math
import os
import struct
import wave

SAMPLE_RATE = 44100
PEAK = 26000


def _note(freq, duration):
    """生成一个带平滑包络的音符采样片段。"""
    n = int(SAMPLE_RATE * duration)
    out = []
    for i in range(n):
        t = i / SAMPLE_RATE
        # 5ms 起音、指数衰减，避免爆音且听感柔和
        attack = min(1.0, t / 0.005)
        decay = math.exp(-3.0 * t / duration)
        env = attack * decay
        # 基频 + 少量二次谐波，声音更像铃音
        sample = math.sin(2 * math.pi * freq * t) + 0.22 * math.sin(4 * math.pi * freq * t)
        out.append(sample * env)
    return out


def build(notes):
    """notes: [(频率, 时长)]，依次播放形成明确的上行或下行。"""
    samples = []
    for freq, duration in notes:
        samples.extend(_note(freq, duration))
    peak = max(abs(s) for s in samples) or 1.0
    scale = PEAK / peak
    samples = [int(s * scale) for s in samples]
    # 末尾留 60ms 静音，避免播放被截断
    samples.extend([0] * int(SAMPLE_RATE * 0.06))
    return samples


def write_wav(path, samples):
    with wave.open(path, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        frames = b''.join(struct.pack('<h', max(-32768, min(32767, s))) for s in samples)
        w.writeframes(frames)


def main():
    base = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'sound')
    os.makedirs(base, exist_ok=True)

    # 上行：C5 -> E5 -> G5 -> C6
    up = build([(523.25, 0.16), (659.25, 0.16), (783.99, 0.16), (1046.50, 0.26)])
    # 下行：C6 -> G5 -> E5 -> C5
    down = build([(1046.50, 0.16), (783.99, 0.16), (659.25, 0.16), (523.25, 0.26)])

    write_wav(os.path.join(base, 's_start_up.wav'), up)
    write_wav(os.path.join(base, 's_end_down.wav'), down)
    print('generated:', 's_start_up.wav', 's_end_down.wav')


if __name__ == '__main__':
    main()
