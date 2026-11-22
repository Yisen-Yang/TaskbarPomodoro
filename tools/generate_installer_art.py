# -*- coding: utf-8 -*-
"""生成 Inno Setup 安装向导配图（深色番茄 · 酷炫风格）。

用法：python tools/generate_installer_art.py
输出：
  docs/images/wizard.png       左侧大图（严格 164x314）
  docs/images/wizard_small.png 右上角小图（严格 55x55）

设计：深夜蓝紫渐变底 + 番茄橙径向光晕 + 发光进度环 + 玻璃质感卡片。
      4x 分辨率绘制后 LANCZOS 缩放，保证在向导里清晰锐利。
"""
import os
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'docs', 'images')
ICON = os.path.join(ROOT, 'assets', 'tomato.png')
FONT_REG = r'C:\Windows\Fonts\msyh.ttc'
FONT_BOLD = r'C:\Windows\Fonts\msyhbd.ttc'

# 4x 绘制再缩小
SCALE = 4
W, H = 164 * SCALE, 314 * SCALE


def f(px):
    return ImageFont.truetype(FONT_BOLD if px[1] else FONT_REG, px[0] * SCALE)


def ft(size, bold=False):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size * SCALE)


def text_center(d, y, text, font, fill):
    box = d.textbbox((0, 0), text, font=font)
    x = (W - (box[2] - box[0])) // 2
    d.text((x, y), text, font=font, fill=fill)


def radial_glow(size, cx, cy, radius, color, strength):
    """生成径向光晕图层。"""
    layer = Image.new('RGBA', size, (0, 0, 0, 0))
    px = layer.load()
    w, h = size
    for yy in range(h):
        for xx in range(w):
            dist = math.hypot(xx - cx, yy - cy)
            if dist < radius:
                a = int(strength * (1 - dist / radius) ** 2)
                px[xx, yy] = (color[0], color[1], color[2], a)
    return layer


def build_wizard():
    # 深色渐变底：顶部深蓝紫 -> 底部近黑
    img = Image.new('RGB', (W, H))
    d = ImageDraw.Draw(img)
    top = (23, 20, 38)      # #171426
    bottom = (10, 9, 18)    # #0a0912
    for y in range(H):
        t = y / (H - 1)
        c = tuple(int(top[i] * (1 - t) + bottom[i] * t) for i in range(3))
        d.line([(0, y), (W, y)], fill=c)

    img = img.convert('RGBA')

    # 番茄橙径向光晕（顶部中心）
    glow = radial_glow((W, H), W // 2, int(H * 0.27), int(W * 0.95),
                       (255, 106, 74), 120)
    img = Image.alpha_composite(img, glow)
    # 一层柔和模糊的暖光，增强"发光"感
    soft = glow.filter(ImageFilter.GaussianBlur(18 * SCALE))
    img = Image.alpha_composite(img, soft)

    d = ImageDraw.Draw(img)

    # 顶部两侧装饰光点
    for cx, cy, rr, col in [
        (int(W * 0.12), int(H * 0.10), 3, (255, 150, 110, 200)),
        (int(W * 0.88), int(H * 0.16), 2, (255, 200, 150, 180)),
        (int(W * 0.20), int(H * 0.72), 2, (160, 150, 255, 140)),
    ]:
        r = rr * SCALE
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col)

    # 发光进度环（套在番茄图标外圈）
    cx, cy = W // 2, int(H * 0.27)
    ring_r = int(W * 0.37)
    # 底环
    d.ellipse((cx - ring_r, cy - ring_r, cx + ring_r, cy + ring_r),
              outline=(255, 255, 255, 28), width=2 * SCALE)
    # 进度弧（番茄橙），用多段模拟渐变发光
    for i in range(38):
        a0 = -90 + i * 6
        a1 = a0 + 8
        alpha = int(120 + 135 * (i / 38))
        d.arc((cx - ring_r, cy - ring_r, cx + ring_r, cy + ring_r),
              start=a0, end=a1, fill=(255, 130 - i, 90, alpha), width=3 * SCALE)

    # 番茄图标（带柔光阴影）
    icon = Image.open(ICON).convert('RGBA')
    isize = int(W * 0.50)
    icon = icon.resize((isize, isize), Image.LANCZOS)
    ix, iy = cx - isize // 2, cy - isize // 2
    # 阴影
    shadow = Image.new('RGBA', img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.ellipse((ix + 4 * SCALE, iy + 8 * SCALE,
                ix + isize + 4 * SCALE, iy + isize + 8 * SCALE),
               fill=(0, 0, 0, 110))
    shadow = shadow.filter(ImageFilter.GaussianBlur(6 * SCALE))
    img = Image.alpha_composite(img, shadow)
    img.alpha_composite(icon, (ix, iy))
    d = ImageDraw.Draw(img)

    # 标题
    text_center(d, int(H * 0.470), '任务栏番茄钟',
                ft(20, True), (255, 255, 255, 255))
    # 副标题（与主标题留出足够间距，避免重叠）
    text_center(d, int(H * 0.555), '专注每一刻 · 高效每一天',
                ft(10), (198, 190, 210, 255))

    # 分隔渐隐线
    d.rounded_rectangle((W // 2 - 40 * SCALE, int(H * 0.605),
                         W // 2 + 40 * SCALE, int(H * 0.605) + 2 * SCALE),
                        radius=SCALE, fill=(255, 120, 90, 150))

    # 底部：三个小胶囊（时间点 / 休息 / 循环 的抽象表示）
    cap_y = int(H * 0.685)
    cap_w, cap_h, gap = 26 * SCALE, 6 * SCALE, 8 * SCALE
    total = cap_w * 3 + gap * 2
    x0 = (W - total) // 2
    colors = [(255, 110, 80, 235), (255, 165, 110, 210), (120, 210, 170, 200)]
    for i in range(3):
        x = x0 + i * (cap_w + gap)
        d.rounded_rectangle((x, cap_y, x + cap_w, cap_y + cap_h),
                            radius=3 * SCALE, fill=colors[i])

    # 底部版本
    text_center(d, int(H * 0.90), 'v1.2.0',
                ft(11, True), (150, 142, 170, 220))

    path = os.path.join(OUT, 'wizard.png')
    final = img.convert('RGB').resize((164, 314), Image.LANCZOS)
    final.save(path)
    print('saved', path, final.size)


def build_small():
    S = 55 * SCALE
    img = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # 深色圆底 + 番茄橙描边
    d.ellipse((2 * SCALE, 2 * SCALE, S - 2 * SCALE, S - 2 * SCALE),
              fill=(23, 20, 38, 255))
    d.ellipse((2 * SCALE, 2 * SCALE, S - 2 * SCALE, S - 2 * SCALE),
              outline=(255, 130, 95, 220), width=2 * SCALE)
    icon = Image.open(ICON).convert('RGBA').resize((int(S * 0.66), int(S * 0.66)), Image.LANCZOS)
    iw = int(S * 0.66)
    img.alpha_composite(icon, ((S - iw) // 2, (S - iw) // 2))
    path = os.path.join(OUT, 'wizard_small.png')
    final = img.resize((55, 55), Image.LANCZOS)
    final.save(path)
    print('saved', path, final.size)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    build_wizard()
    build_small()
