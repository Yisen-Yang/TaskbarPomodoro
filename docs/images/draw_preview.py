# -*- coding: utf-8 -*-
"""生成 README 用的高仿真界面示意图（纯 Pillow，无需运行软件）。
按钮图标用几何图形绘制，避免字体缺字显示成方块。"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, os

OUT = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(OUT))
TOMATO = os.path.join(ROOT, 'assets', 'tomato.png')  # 与软件完全相同的番茄图标
FONT = "C:/Windows/Fonts/msyh.ttc"
FONT_BD = "C:/Windows/Fonts/msyhbd.ttc"


def paste_tomato(img, x, y, size):
    """把软件同款番茄图标贴到 (x, y)，尺寸 size×size。"""
    t = Image.open(TOMATO).convert('RGBA').resize((size, size), Image.LANCZOS)
    img.paste(t, (x, y), t)

def f(size, bold=False):
    try:
        return ImageFont.truetype(FONT_BD if bold else FONT, size)
    except Exception:
        return ImageFont.load_default()

def rounded(draw, box, r, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)

def draw_ring(d, cx, cy, radius, progress, color, width=5):
    box = (cx-radius, cy-radius, cx+radius, cy+radius)
    d.arc(box, start=0, end=360, fill=(62,66,86,255), width=width)
    if progress > 0:
        d.arc(box, start=-90, end=-90+360*progress, fill=color, width=width)
    d.ellipse((cx-3,cy-3,cx+3,cy+3), fill=(255,255,255,205))

def draw_play(d, cx, cy, color):
    d.polygon([(cx-5,cy-8),(cx-5,cy+8),(cx+7,cy)], fill=color)

def draw_pause(d, cx, cy, color):
    d.rounded_rectangle((cx-7,cy-8,cx-3,cy+8),radius=2,fill=color)
    d.rounded_rectangle((cx+3,cy-8,cx+7,cy+8),radius=2,fill=color)

def draw_reset(d, cx, cy, color):
    d.arc((cx-9,cy-9,cx+9,cy+9), start=40, end=320, fill=color, width=3)
    d.polygon([(cx-11,cy-3),(cx-4,cy-6),(cx-6,cy+2)], fill=color)

def draw_pin(d, cx, cy, color):
    d.ellipse((cx-5,cy-10,cx+5,cy-1), fill=color)
    d.line((cx,cy-1,cx,cy+9), fill=color, width=3)
    d.line((cx-6,cy+9,cx+6,cy+9), fill=color, width=2)

def mini_panel(img, box, work=True, progress=0.62, time_txt="18:42", playing=True):
    """状态卡片用的精简窗口：圆环 + 时间 + 播放/暂停按钮"""
    d = ImageDraw.Draw(img, "RGBA")
    x0,y0,x1,y1 = box
    cy=(y0+y1)//2
    for y in range(y0,y1):
        t=(y-y0)/max(1,y1-y0)
        c0,c1=((26,26,36),(20,20,30)) if work else ((20,40,30),(16,30,24))
        d.line([(x0,y),(x1,y)],fill=(int(c0[0]+(c1[0]-c0[0])*t),
                                     int(c0[1]+(c1[1]-c0[1])*t),
                                     int(c0[2]+(c1[2]-c0[2])*t),215))
    rounded(d,box,10,None,outline=(110,116,140,255),width=1)
    color=(255,120,95,255) if work else (90,215,155,255)
    ring_r=17; rx=x0+16+ring_r
    draw_ring(d,rx,cy,ring_r,progress,color)
    d.text((rx+ring_r+14,cy-14),time_txt,font=f(25,True),fill=(255,255,255,245))
    bx=x1-30
    if playing: draw_pause(d,bx,cy,(255,255,255,235))
    else: draw_play(d,bx,cy,(255,255,255,235))

def panel(img, box, work=True, progress=0.62, time_txt="18:42", preset="25/5", playing=True):
    d = ImageDraw.Draw(img, "RGBA")
    x0, y0, x1, y1 = box
    h = y1 - y0
    for y in range(y0, y1):
        t = (y - y0) / max(1, h)
        c0, c1 = ((26,26,36),(20,20,30)) if work else ((20,40,30),(16,30,24))
        d.line([(x0,y),(x1,y)], fill=(int(c0[0]+(c1[0]-c0[0])*t),
                                      int(c0[1]+(c1[1]-c0[1])*t),
                                      int(c0[2]+(c1[2]-c0[2])*t), 210))
    rounded(d, box, 11, None, outline=(110,116,140,255), width=1)
    d.line([(x0+12,y0+1),(x1-12,y0+1)], fill=(90,96,120,255), width=1)

    cy = (y0+y1)//2
    pad = 15
    color = (255,120,95,255) if work else (90,215,155,255)
    ring_r = 17
    rx = x0+pad+ring_r
    draw_ring(d, rx, cy, ring_r, progress, color)

    tx = rx+ring_r+14
    d.text((tx, cy-14), time_txt, font=f(25,True), fill=(255,255,255,245))

    # 右侧按钮区（自右向左排布）
    right = x1 - pad
    # 预设下拉
    d.rounded_rectangle((right-52,cy-14,right,cy+14), radius=6, fill=(70,74,92,255))
    d.text((right-46,cy-11), preset, font=f(14), fill=(255,255,255,225))
    d.polygon([(right-10,cy-1),(right-4,cy-1),(right-7,cy+4)], fill=(255,255,255,170))
    # 图钉 / 重置 / 播放
    draw_pin(d, right-74, cy, (255,255,255,225))
    draw_reset(d, right-106, cy, (255,255,255,225))
    if playing:
        draw_pause(d, right-138, cy, (255,255,255,235))
    else:
        draw_play(d, right-138, cy, (255,255,255,235))

# ── 主图 ────────────────────────────────────────────────────
W, H = 1200, 640
img = Image.new("RGBA",(W,H),(0,0,0,255))
d = ImageDraw.Draw(img,"RGBA")
for y in range(H-90):
    t=y/(H-90)
    d.line([(0,y),(W,y)], fill=(int(22+14*t),int(26+10*t),int(42+6*t),255))
for cx,cy,rad,col in [(980,170,280,(70,90,160,30)),(220,460,240,(120,70,140,22))]:
    glow=Image.new("RGBA",(W,H),(0,0,0,0)); gd=ImageDraw.Draw(glow)
    gd.ellipse((cx-rad,cy-rad,cx+rad,cy+rad),fill=col)
    img=Image.alpha_composite(img,glow.filter(ImageFilter.GaussianBlur(80)))
d=ImageDraw.Draw(img,"RGBA")

paste_tomato(img, 64, 50, 64)
d.text((142,58),"任务栏番茄钟",font=f(56,True),fill=(255,255,255,250))
d.text((66,132),"常驻任务栏 · 专注与休息，抬眼即见",font=f(25),fill=(185,195,220,235))

# 特性标签
tags=[("始终置顶","不被任何窗口遮挡"),("跨屏自适应","拖动到不同分辨率不变形"),("零依赖","仅 PySide6，EXE 约 44MB")]
tx=66
for title,sub in tags:
    rounded(d,(tx,210,tx+300,286),14,(38,42,58,255),outline=(78,84,108,255),width=1)
    d.text((tx+18,226),title,font=f(21,True),fill=(255,255,255,240))
    d.text((tx+18,256),sub,font=f(15),fill=(170,182,208,225))
    tx+=320

# 任务栏
tb_y0=H-90
d.rectangle((0,tb_y0,W,H),fill=(32,34,44,255))
d.line([(0,tb_y0),(W,tb_y0)],fill=(70,74,92,255),width=1)
d.text((30,tb_y0+26),"⊞",font=f(36),fill=(235,240,255,230))
d.ellipse((104,tb_y0+29,130,tb_y0+55),outline=(200,210,235,180),width=2)
d.line((124,tb_y0+49,133,tb_y0+58),fill=(200,210,235,180),width=2)
# 固定在任务栏的番茄钟应用图标（同款番茄）+ 运行指示条
paste_tomato(img, 152, tb_y0+22, 36)
d.rounded_rectangle((158,tb_y0+62,182,tb_y0+65),radius=2,fill=(255,120,95,235))
# 焦点窗口放大展示
panel(img,(330,tb_y0+14,770,tb_y0+74),work=True,progress=0.62,time_txt="18:42",playing=True)
# 标注
d.line((550,tb_y0+12,550,tb_y0-46),fill=(255,140,110,210),width=2)
d.ellipse((546,tb_y0-50,554,tb_y0-42),fill=(255,140,110,255))
d.text((438,tb_y0-86),"半透明玻璃质感 · 与任务栏同高",font=f(19),fill=(255,190,170,240))

img.convert("RGB").save(os.path.join(OUT,"hero.png"),quality=95)
print("hero.png saved")

# ── 状态图 ──────────────────────────────────────────────────
W2,H2=1200,520
img2=Image.new("RGBA",(W2,H2),(18,20,30,255))
d2=ImageDraw.Draw(img2,"RGBA")
paste_tomato(img2, 60, 38, 44)
d2.text((116,44),"专注状态一览",font=f(40,True),fill=(255,255,255,248))
cards=[
    (60,"专注中","圆环实时显示进度\n倒计时精确到秒",True,0.62,"18:42",True),
    (460,"短休息","每轮专注后\n自动进入 5 分钟短休",False,0.35,"04:16",False),
    (860,"长休息","每 4 个番茄\n自动进入 15 分钟长休",False,0.72,"12:05",False),
]
for x,title,desc,work,prog,tm,playing in cards:
    rounded(d2,(x,120,x+320,440),16,(32,36,50,255),outline=(72,78,102,255),width=1)
    d2.text((x+24,148),title,font=f(26,True),fill=(255,255,255,245))
    mini_panel(img2,(x+20,206,x+300,266),work=work,progress=prog,time_txt=tm,playing=playing)
    for i,line in enumerate(desc.split("\n")):
        d2.text((x+24,308+i*32),line,font=f(19),fill=(178,190,215,235))
img2.convert("RGB").save(os.path.join(OUT,"states.png"),quality=95)
print("states.png saved")
