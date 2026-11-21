# -*- coding: utf-8 -*-
"""生成 README 用的白底示意图（使用真实软件截图素材）。

先用 venv 运行 tools/capture_ui.py 抓取真实界面到 docs/images/_capture/，
再用系统 Python（需 Pillow）运行本脚本生成 hero.png / states.png。
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

OUT = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(OUT))
CAP = os.path.join(OUT, "_capture")
TOMATO = os.path.join(ROOT, "assets", "tomato.png")
FONT = "C:/Windows/Fonts/msyh.ttc"
FONT_BD = "C:/Windows/Fonts/msyhbd.ttc"

# 白底配色
BG_TOP = (255, 255, 255)
BG_BOTTOM = (244, 247, 251)
INK = (29, 35, 48)
MUTED = (108, 118, 136)
ACCENT = (238, 92, 66)
LINE = (224, 230, 239)
CARD = (255, 255, 255)


def f(size, bold=False):
    try:
        return ImageFont.truetype(FONT_BD if bold else FONT, size)
    except Exception:
        return ImageFont.load_default()


def paste_tomato(img, x, y, size):
    t = Image.open(TOMATO).convert('RGBA').resize((size, size), Image.LANCZOS)
    img.paste(t, (x, y), t)


def capture(name, trim=0):
    p = os.path.join(CAP, name)
    if not os.path.exists(p):
        raise FileNotFoundError("缺少截图素材：%s（请先运行 tools/capture_ui.py）" % p)
    im = Image.open(p).convert('RGBA')
    if trim:
        im = im.crop((trim, trim, im.width - trim, im.height - trim))
    return im


def shadow(img, box, radius=18, blur=18, alpha=36, offset=(0, 6)):
    """在 img 上为 box 区域画柔和阴影。"""
    layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x0, y0, x1, y1 = box
    ox, oy = offset
    d.rounded_rectangle((x0 + ox, y0 + oy, x1 + ox, y1 + oy), radius=radius,
                        fill=(20, 30, 50, alpha))
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    img.alpha_composite(layer)


def card(img, box, radius=18, fill=CARD, outline=LINE, sd=True):
    if sd:
        shadow(img, box, radius=radius)
    d = ImageDraw.Draw(img, 'RGBA')
    d.rounded_rectangle(box, radius=radius, fill=fill + (255,),
                        outline=outline + (255,), width=2)


def fit(im, max_w, max_h):
    im = im.copy()
    im.thumbnail((max_w, max_h), Image.LANCZOS)
    return im


def background(w, h):
    img = Image.new('RGBA', (w, h), BG_TOP + (255,))
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = y / max(1, h - 1)
        d.line([(0, y), (w, y)], fill=tuple(int(BG_TOP[i] + (BG_BOTTOM[i] - BG_TOP[i]) * t)
                                            for i in range(3)) + (255,))
    # 顶部极淡的番茄色光晕
    glow = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((w - 420, -260, w + 120, 300), fill=(238, 92, 66, 16))
    glow = glow.filter(ImageFilter.GaussianBlur(90))
    img.alpha_composite(glow)
    return img


def draw_header(img, title, subtitle):
    d = ImageDraw.Draw(img, 'RGBA')
    paste_tomato(img, 72, 62, 66)
    d.text((158, 58), title, font=f(52, True), fill=INK + (255,))
    d.text((160, 130), subtitle, font=f(23), fill=MUTED + (255,))


# ── hero.png ────────────────────────────────────────────────
W, H = 1440, 860
img = background(W, H)
draw_header(img, "任务栏番茄钟", "常驻任务栏 · 专注与休息，抬眼即见")

tags = [
    ("始终置顶", "不被任何窗口遮挡"),
    ("跨屏自适应", "不同分辨率拖动不变形"),
    ("多语言 · 多主题", "中 / 英 / 日，5 套外观随手换"),
]
tx = 72
for title, sub in tags:
    card(img, (tx, 200, tx + 408, 302), radius=16)
    d = ImageDraw.Draw(img, 'RGBA')
    d.ellipse((tx + 22, 228, tx + 30, 236), fill=ACCENT + (255,))
    d.text((tx + 44, 220), title, font=f(23, True), fill=INK + (255,))
    d.text((tx + 44, 258), sub, font=f(16), fill=MUTED + (255,))
    tx += 432

# 主窗口展示区（真实截图）
card(img, (72, 344, 1368, 566), radius=20)
d = ImageDraw.Draw(img, 'RGBA')
d.text((104, 368), "与任务栏同高的玻璃质感小窗", font=f(18, True), fill=INK + (255,))
main = capture("light_work.png", trim=12)
main = fit(main, 1160, 140)
# 圆角遮罩，贴到白底卡片上
mask = Image.new('L', main.size, 0)
ImageDraw.Draw(mask).rounded_rectangle((0, 0, main.width, main.height), radius=16, fill=255)
main.putalpha(mask)
img.alpha_composite(main, (140, 410))

# 小图：右键菜单 + 设置窗口
card(img, (72, 598, 520, 830), radius=20)
menu = capture("menu.png")
menu = fit(menu, 180, 190)
mmask = Image.new('L', menu.size, 0)
ImageDraw.Draw(mmask).rounded_rectangle((0, 0, menu.width, menu.height), radius=10, fill=255)
menu.putalpha(mmask)
img.alpha_composite(menu, (100, 622))
d = ImageDraw.Draw(img, 'RGBA')
d.text((310, 636), "右键菜单", font=f(22, True), fill=INK + (255,))
for i, line in enumerate(["开始 / 暂停 · 重置", "连续专注 · 今日统计", "设置 · 显隐 · 退出"]):
    d.text((310, 684 + i * 34), line, font=f(16), fill=MUTED + (255,))

card(img, (552, 598, 1368, 830), radius=20)
settings = capture("settings.png")
# 裁掉大段留白，只取上半部分
settings = settings.crop((0, 0, settings.width, int(settings.height * 0.72)))
settings = fit(settings, 300, 200)
smask = Image.new('L', settings.size, 0)
ImageDraw.Draw(smask).rounded_rectangle((0, 0, settings.width, settings.height), radius=10, fill=255)
settings.putalpha(smask)
img.alpha_composite(settings, (580, 616))
d = ImageDraw.Draw(img, 'RGBA')
d.text((910, 636), "设置窗口", font=f(22, True), fill=INK + (255,))
for i, line in enumerate(["时长 / 长休息 · 连续专注", "5 套主题 · 16 种音效", "界面语言即时切换"]):
    d.text((910, 684 + i * 34), line, font=f(16), fill=MUTED + (255,))

img.convert('RGB').save(os.path.join(OUT, 'hero.png'), quality=95)
print('hero.png saved')

# ── states.png ──────────────────────────────────────────────
W2, H2 = 1440, 560
img2 = background(W2, H2)
draw_header(img2, "专注状态一览", "三种状态，一眼分清现在该做什么")

cards = [
    ("专注中", "light_work.png", "红色进度环实时推进", "倒计时精确到秒", ACCENT),
    ("短休息", "light_break.png", "每轮专注后自动进入", "5 分钟短休息", (60, 176, 128)),
    ("长休息", "light_longbreak.png", "每 4 个番茄自动进入", "15 分钟长休息", (72, 138, 214)),
]
cx = 72
for title, shot, line1, line2, color in cards:
    card(img2, (cx, 200, cx + 408, 490), radius=20)
    d2 = ImageDraw.Draw(img2, 'RGBA')
    d2.rounded_rectangle((cx + 24, 228, cx + 32, 236), radius=4, fill=color + (255,))
    d2.text((cx + 46, 220), title, font=f(25, True), fill=INK + (255,))
    win = capture(shot, trim=8)
    win = fit(win, 356, 60)
    wmask = Image.new('L', win.size, 0)
    ImageDraw.Draw(wmask).rounded_rectangle((0, 0, win.width, win.height), radius=12, fill=255)
    win.putalpha(wmask)
    img2.alpha_composite(win, (cx + 26, 280))
    d2.text((cx + 26, 380), line1, font=f(18), fill=INK + (255,))
    d2.text((cx + 26, 416), line2, font=f(18), fill=MUTED + (255,))
    cx += 432

img2.convert('RGB').save(os.path.join(OUT, 'states.png'), quality=95)
print('states.png saved')
