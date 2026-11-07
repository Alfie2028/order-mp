# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageFont

FONT = "C:/Windows/Fonts/msyh.ttc"

def font(sz):
    return ImageFont.truetype(FONT, sz)

FW, FH = 268, 566
W = 20 * 4 + FW * 3
H = 60 + FH + 46
img = Image.new("RGB", (W, H), (244, 246, 251))
d = ImageDraw.Draw(img)

def text(x, y, s, sz=13, fill=(31, 36, 48)):
    d.text((x, y), s, font=font(sz), fill=fill)

def panel(x, title, tcolor, mode, note, ncolor):
    y = 46
    d.rounded_rectangle([x, y, x + FW, y + FH], radius=14, fill=(255, 255, 255), outline=(214, 221, 233))
    text(x + 8, y - 30, title, 16, tcolor)

    hy = y + 10
    d.rounded_rectangle([x + 10, hy, x + FW - 10, hy + 86], radius=10, fill=(9, 44, 150))
    text(x + 20, hy + 8, "商家工作台", 13, (255, 255, 255))
    sw = (FW - 40 - 16) / 3
    for i, (n, l) in enumerate([("2", "待接订单"), ("4", "今日订单"), ("¥71.20", "今日流水")]):
        sx = x + 20 + i * (sw + 8)
        d.rounded_rectangle([sx, hy + 30, sx + sw, hy + 72], radius=7, fill=(38, 80, 180))
        text(sx + 6, hy + 34, n, 14, (255, 255, 255))
        text(sx + 6, hy + 56, l, 9, (200, 215, 245))

    ty = hy + 96
    d.rounded_rectangle([x + 10, ty, x + FW - 10, ty + 26], radius=7, fill=(52, 40, 88))
    text(x + 18, ty + 6, "● 已打烊", 10, (255, 255, 255))
    text(x + FW - 78, ty + 7, "点击开张", 9, (210, 200, 230))

    ey = ty + 36

    if mode == "bad":
        for i, name in enumerate(["餐品管理", "档口管理", "优惠券", "营业看板", "用户评价"]):
            cy = ey + i * 40
            cw = int(FW * 0.58)
            d.rounded_rectangle([x + 12, cy, x + 12 + cw, cy + 34], radius=7, fill=(248, 250, 254), outline=(227, 232, 241))
            text(x + 22, cy + 8, name, 11, (65, 80, 110))
            text(x + 12 + cw - 20, cy + 8, ">", 11, (6, 55, 201))
        oy = ey + 5 * 40 + 4
        d.rounded_rectangle([x + 12, oy, x + FW - 12, oy + 34], radius=7, fill=(238, 242, 250))
        text(x + 22, oy + 9, "订单列表（被压到最下）", 10, (91, 100, 120))

    elif mode == "a":
        cw = (FW - 24 - 8) / 2
        for i, name in enumerate(["餐品管理", "档口管理", "优惠券", "用户评价"]):
            cx = x + 12 + (i % 2) * (cw + 8)
            cy = ey + (i // 2) * 40
            d.rounded_rectangle([cx, cy, cx + cw, cy + 34], radius=7, fill=(242, 247, 255), outline=(216, 228, 245))
            text(cx + cw / 2 - 22, cy + 8, name, 11, (6, 55, 201))
        oy = ey + 2 * 40 + 4
        d.rounded_rectangle([x + 12, oy, x + FW - 12, oy + 40], radius=7, fill=(231, 246, 236))
        text(x + 22, oy + 13, "订单列表（上移，紧接入口）", 10, (31, 157, 85))

    else:
        cw = (FW - 24 - 12) / 4
        for i, (ic, name) in enumerate([("▣", "餐品"), ("▤", "档口"), ("◎", "券"), ("★", "评价")]):
            cx = x + 12 + i * (cw + 4)
            d.rounded_rectangle([cx, ey, cx + cw, ey + 40], radius=7, fill=(242, 247, 255))
            text(cx + cw / 2 - 6, ey + 5, ic, 12, (6, 55, 201))
            text(cx + cw / 2 - 10, ey + 24, name, 9, (6, 55, 201))
        oy = ey + 46
        d.rounded_rectangle([x + 12, oy, x + FW - 12, oy + 56], radius=7, fill=(231, 246, 236))
        text(x + 22, oy + 20, "订单列表（获得更多空间）", 10, (31, 157, 85))

    gy = y + FH - 96
    for i, (t, act) in enumerate([("待接单", True), ("制作中", False), ("待取餐", False), ("已完成", False)]):
        tx = x + 12 + i * 61
        d.rounded_rectangle([tx, gy, tx + 56, gy + 22], radius=11, fill=(9, 44, 150) if act else (255, 255, 255), outline=(230, 234, 242))
        text(tx + 10, gy + 4, t, 9, (255, 255, 255) if act else (120, 130, 150))

    oy2 = gy + 32
    d.rounded_rectangle([x + 10, oy2, x + FW - 10, oy2 + 66], radius=9, fill=(255, 255, 255), outline=(226, 231, 240))
    text(x + 20, oy2 + 8, "订单号 XC20261106844835", 9, (31, 36, 48))
    text(x + 20, oy2 + 24, "鱼香肉丝盖饭 x 1", 9, (91, 100, 120))
    text(x + 20, oy2 + 42, "取餐码 1004", 10, (9, 40, 120))
    d.rounded_rectangle([x + FW - 92, oy2 + 36, x + FW - 22, oy2 + 58], radius=11, fill=(9, 72, 201))
    text(x + FW - 78, oy2 + 42, "接单", 9, (255, 255, 255))

    text(x + 8, y + FH + 10, note, 11, ncolor)

panel(20, "现状 · 问题", (192, 57, 43), "bad", "每行仅 1 张，右侧半屏全空", (192, 57, 43))
panel(308, "方案A · 2x2 四宫格", (31, 157, 85), "a", "去重后 4 个正好铺满", (31, 157, 85))
panel(596, "方案B · 图标条 + 订单优先", (6, 55, 201), "b", "入口更紧凑，一进页就见待接单", (6, 55, 201))

out = r"E:\ClaudeCode\projects\移动课设\docs\商家工作台入口重设计对比.png"
img.save(out)
print("SAVED", out)
