#!/usr/bin/env python3
"""
Build HomeRun Epic 001 "Accident" as a 9:16 daylight anime promo.

The anime keyframes are produced by the local image-gen-web project and kept in
the Job 003 export folder. This script only composites, animates, captions,
places real HomeRun product screenshots, and encodes the archived assets.
"""

from __future__ import annotations

import argparse
import json
import math
import subprocess
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps


W, H = 1080, 1920
FPS = 24
SR = 48_000
FFMPEG = Path("/opt/homebrew/bin/ffmpeg")
FFPROBE = Path("/opt/homebrew/bin/ffprobe")

INK = (24, 39, 55)
INK_SOFT = (65, 83, 101)
PANEL = (255, 255, 250)
PANEL_SOFT = (250, 253, 248)
WHITE = (255, 255, 255)
NAVY = (27, 55, 92)
NAVY_DEEP = (12, 27, 48)
ORANGE = (241, 138, 52)
ORANGE_SOFT = (255, 187, 96)
GREEN = (50, 163, 117)
GREEN_SOFT = (111, 205, 163)
RED = (221, 78, 73)
BLUE = (66, 145, 212)
SKY = (127, 190, 231)
DIRT = (191, 134, 80)
LINE = (214, 224, 228)

PRODUCTS: dict[str, Image.Image] = {}
PRODUCT_CACHE: dict[tuple[str, int, int], Image.Image] = {}


@dataclass(frozen=True)
class Scene:
    key: str
    duration: float
    bg: str
    subtitle: str
    title: str = ""
    overlay: str = "default"
    start_pos: tuple[float, float] = (0.5, 0.5)
    end_pos: tuple[float, float] = (0.5, 0.5)
    wash: tuple[int, int, int] = WHITE
    wash_alpha: int = 18


def repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def out_dirs(root: Path) -> dict[str, Path]:
    job_work = root / "HomeRun/05_working_files/job-003-anime-episode-001-production"
    job_export = root / "HomeRun/06_exports/job-003-anime-episode-001-production"
    return {
        "work": job_work,
        "export": job_export,
        "audio": job_export / "audio",
        "videos": job_export / "videos",
        "scenes": job_export / "scenes/v0.2",
        "keyframes": job_export / "keyframes/v0.2",
        "product": job_work / "source-assets/product-070",
    }


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/System/Library/Fonts/STHeiti Medium.ttc" if bold else "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/PingFang.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
    ]
    for item in candidates:
        if item and Path(item).exists():
            return ImageFont.truetype(item, size=size)
    return ImageFont.load_default()


F_DISPLAY = font(92, True)
F_H1 = font(68, True)
F_H2 = font(52, True)
F_BODY = font(43)
F_BODY_B = font(43, True)
F_SMALL = font(32)
F_SMALL_B = font(32, True)
F_TINY = font(25)
F_TINY_B = font(25, True)
F_MICRO = font(21)
F_MICRO_B = font(21, True)


def clamp(v: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, v))


def ease_out_cubic(t: float) -> float:
    t = clamp(t)
    return 1 - (1 - t) ** 3


def ease_in_out(t: float) -> float:
    t = clamp(t)
    return t * t * (3 - 2 * t)


def pulse(t: float, speed: float = 1.0) -> float:
    return 0.5 + 0.5 * math.sin(t * math.tau * speed)


def cover_resize(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    target_w, target_h = size
    scale = max(target_w / img.width, target_h / img.height)
    resized = img.resize((math.ceil(img.width * scale), math.ceil(img.height * scale)), Image.Resampling.LANCZOS)
    x = (resized.width - target_w) // 2
    y = (resized.height - target_h) // 2
    return resized.crop((x, y, x + target_w, y + target_h))


def contain_on_canvas(img: Image.Image, size: tuple[int, int], bg=(255, 255, 255, 255)) -> Image.Image:
    target_w, target_h = size
    scale = min(target_w / img.width, target_h / img.height)
    new_size = (max(1, int(img.width * scale)), max(1, int(img.height * scale)))
    resized = img.convert("RGBA").resize(new_size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", size, bg)
    canvas.alpha_composite(resized, ((target_w - new_size[0]) // 2, (target_h - new_size[1]) // 2))
    return canvas


def prepare_bg(path: Path, zoom: float = 1.10) -> Image.Image:
    img = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    target = (math.ceil(W * zoom), math.ceil(H * zoom))
    img = cover_resize(img, target)
    img = ImageEnhance.Brightness(img).enhance(1.06)
    img = ImageEnhance.Contrast(img).enhance(1.02)
    img = ImageEnhance.Color(img).enhance(1.08)
    return img


def crop_pan(img: Image.Image, p: float, start: tuple[float, float], end: tuple[float, float]) -> Image.Image:
    px = start[0] + (end[0] - start[0]) * ease_in_out(p)
    py = start[1] + (end[1] - start[1]) * ease_in_out(p)
    max_x = max(0, img.width - W)
    max_y = max(0, img.height - H)
    x = int(max_x * clamp(px))
    y = int(max_y * clamp(py))
    return img.crop((x, y, x + W, y + H))


def overlay_tint(frame: Image.Image, color: tuple[int, int, int], alpha: int) -> None:
    if alpha <= 0:
        return
    frame.alpha_composite(Image.new("RGBA", (W, H), color + (alpha,)))


def make_bottom_readability() -> Image.Image:
    y = np.linspace(0, 1, H, dtype=np.float32)[:, None]
    bottom = np.clip((y - 0.68) / 0.32, 0, 1) ** 1.7
    top = np.clip((0.18 - y) / 0.18, 0, 1) ** 1.4
    alpha = (bottom * 62 + top * 24).astype(np.uint8)
    alpha = np.repeat(alpha, W, axis=1)
    arr = np.zeros((H, W, 4), dtype=np.uint8)
    arr[..., 0] = 255
    arr[..., 1] = 255
    arr[..., 2] = 250
    arr[..., 3] = alpha
    return Image.fromarray(arr, "RGBA")


READABILITY = make_bottom_readability()


def rounded(draw: ImageDraw.ImageDraw, xy: tuple[int, int, int, int], radius: int, fill, outline=None, width: int = 1) -> None:
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def text_size(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.ImageFont) -> tuple[int, int]:
    if not text:
        return (0, 0)
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0], box[3] - box[1]


def wrap_text(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.ImageFont, max_width: int) -> list[str]:
    lines: list[str] = []
    for raw in text.split("\n"):
        raw = raw.strip()
        if not raw:
            lines.append("")
            continue
        current = ""
        tokens: Iterable[str]
        if " " in raw and sum("\u4e00" <= c <= "\u9fff" for c in raw) < len(raw) / 2:
            tokens = [token + " " for token in raw.split(" ")]
        else:
            tokens = list(raw)
        for token in tokens:
            candidate = current + token
            if text_size(draw, candidate, fnt)[0] <= max_width or not current:
                current = candidate
            else:
                lines.append(current.rstrip())
                current = token
        if current:
            lines.append(current.rstrip())
    return lines


def draw_wrapped(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    fnt: ImageFont.ImageFont,
    fill,
    max_width: int,
    line_gap: int = 12,
    align: str = "left",
) -> int:
    x, y = xy
    lines = wrap_text(draw, text, fnt, max_width)
    total_h = 0
    for line in lines:
        w, h = text_size(draw, line, fnt)
        tx = x if align == "left" else x + (max_width - w) // 2
        draw.text((tx, y + total_h), line, font=fnt, fill=fill)
        total_h += h + line_gap
    return max(0, total_h - line_gap)


def product_fit(key: str, size: tuple[int, int]) -> Image.Image:
    cache_key = (key, size[0], size[1])
    if cache_key not in PRODUCT_CACHE:
        PRODUCT_CACHE[cache_key] = contain_on_canvas(PRODUCTS[key], size)
    return PRODUCT_CACHE[cache_key]


def paste_rounded(frame: Image.Image, img: Image.Image, box: tuple[int, int, int, int], radius: int) -> None:
    x1, y1, x2, y2 = box
    w, h = x2 - x1, y2 - y1
    if w <= 0 or h <= 0:
        return
    layer = img.resize((w, h), Image.Resampling.LANCZOS).convert("RGBA")
    mask = Image.new("L", (w, h), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle((0, 0, w, h), radius=radius, fill=255)
    alpha = layer.getchannel("A")
    layer.putalpha(Image.composite(alpha, Image.new("L", (w, h), 0), mask))
    frame.alpha_composite(layer, (x1, y1))


def draw_product_panel(
    frame: Image.Image,
    key: str,
    box: tuple[int, int, int, int],
    p: float,
    title: str,
    caption: str = "",
    accent: tuple[int, int, int] = ORANGE,
) -> None:
    p = clamp(p)
    if p <= 0:
        return
    d = ImageDraw.Draw(frame, "RGBA")
    x1, y1, x2, y2 = box
    a = int(255 * p)
    y_off = int((1 - ease_out_cubic(p)) * 42)
    y1 += y_off
    y2 += y_off
    rounded(d, (x1 + 8, y1 + 12, x2 + 8, y2 + 12), 34, (20, 32, 42, int(56 * p)), None)
    rounded(d, (x1, y1, x2, y2), 34, PANEL + (int(244 * p),), (255, 255, 255, int(210 * p)), 3)
    rounded(d, (x1 + 18, y1 + 18, x2 - 18, y1 + 72), 22, (238, 247, 241, int(238 * p)), None)
    d.ellipse((x1 + 38, y1 + 37, x1 + 54, y1 + 53), fill=accent + (a,))
    d.text((x1 + 70, y1 + 30), title, font=F_MICRO_B, fill=INK + (a,))
    if caption:
        d.text((x1 + 70, y1 + 54), caption, font=F_MICRO, fill=INK_SOFT + (int(220 * p),))
    inner = (x1 + 18, y1 + 86, x2 - 18, y2 - 18)
    img = product_fit(key, (inner[2] - inner[0], inner[3] - inner[1]))
    paste_rounded(frame, img, inner, 24)
    rounded(d, inner, 24, None, LINE + (int(220 * p),), 2)


def draw_top_bar(frame: Image.Image, t_abs: float, score: str) -> None:
    d = ImageDraw.Draw(frame, "RGBA")
    rounded(d, (42, 36, W - 42, 124), 24, PANEL + (235,), (255, 255, 255, 190), 2)
    d.text((70, 58), "HomeRun", font=F_SMALL_B, fill=ORANGE + (255,))
    d.text((232, 61), "EPIC 001 / 意外", font=F_TINY_B, fill=INK + (235,))
    d.text((520, 61), "北洲航海家 Voyager  vs  城南流星", font=F_TINY, fill=INK_SOFT + (230,))
    rounded(d, (W - 188, 54, W - 72, 104), 15, NAVY + (245,), None)
    sw, _ = text_size(d, score, F_SMALL_B)
    d.text((W - 130 - sw // 2, 61), score, font=F_SMALL_B, fill=WHITE + (255,))
    progress_w = int((W - 140) * clamp(t_abs / TOTAL_DURATION))
    d.rounded_rectangle((70, 132, 70 + progress_w, 139), radius=3, fill=ORANGE + (220,))
    d.rounded_rectangle((70 + progress_w, 132, W - 70, 139), radius=3, fill=(255, 255, 255, 130))


def draw_subtitle(frame: Image.Image, text: str, scene_title: str = "") -> None:
    d = ImageDraw.Draw(frame, "RGBA")
    panel_x, panel_w = 64, W - 128
    lines = wrap_text(d, text, F_BODY_B, panel_w - 86)
    line_h = 57
    panel_h = max(174, 84 + len(lines) * line_h + (38 if scene_title else 0))
    panel_y = H - panel_h - 72
    rounded(d, (panel_x + 8, panel_y + 12, panel_x + panel_w + 8, panel_y + panel_h + 12), 30, (16, 28, 38, 54), None)
    rounded(d, (panel_x, panel_y, panel_x + panel_w, panel_y + panel_h), 30, PANEL + (238,), (255, 255, 255, 210), 2)
    d.rectangle((panel_x + 28, panel_y + 30, panel_x + 36, panel_y + panel_h - 30), fill=ORANGE + (235,))
    y = panel_y + 28
    if scene_title:
        d.text((panel_x + 58, y), scene_title, font=F_TINY_B, fill=ORANGE + (255,))
        y += 40
    for line in lines:
        d.text((panel_x + 58, y), line, font=F_BODY_B, fill=INK + (255,))
        y += line_h


def draw_title_stack(frame: Image.Image, title: str, kicker: str, p: float, y: int = 242) -> None:
    d = ImageDraw.Draw(frame, "RGBA")
    pp = ease_out_cubic(min(p / 0.55, 1))
    offset = int((1 - pp) * 80)
    alpha = int(255 * pp)
    rounded(d, (58 - offset, y - 26, 172, y + 22), 16, ORANGE + (int(222 * pp),), None)
    d.text((78 - offset, y - 18), kicker, font=F_MICRO_B, fill=WHITE + (alpha,))
    draw_wrapped(d, (72 - offset, y + 34), title, F_DISPLAY, INK + (alpha,), 870, 10)


def draw_chip(frame: Image.Image, xy: tuple[int, int], text: str, p: float, accent=ORANGE, fill=PANEL) -> None:
    if p <= 0:
        return
    d = ImageDraw.Draw(frame, "RGBA")
    x, y = xy
    a = int(245 * clamp(p))
    tw, th = text_size(d, text, F_SMALL_B)
    w = tw + 58
    rounded(d, (x, y, x + w, y + 66), 20, fill + (a,), accent + (int(150 * p),), 2)
    d.text((x + 29, y + 17), text, font=F_SMALL_B, fill=INK + (int(255 * p),))


def draw_info_card(
    frame: Image.Image,
    xy: tuple[int, int],
    title: str,
    value: str,
    caption: str,
    p: float,
    accent=ORANGE,
    w: int = 430,
) -> None:
    p = clamp(p)
    if p <= 0:
        return
    d = ImageDraw.Draw(frame, "RGBA")
    x, y = xy
    y_off = int((1 - ease_out_cubic(p)) * 34)
    a = int(240 * p)
    rounded(d, (x + 6, y + y_off + 10, x + w + 6, y + y_off + 184), 24, (18, 30, 40, int(45 * p)), None)
    rounded(d, (x, y + y_off, x + w, y + y_off + 174), 24, PANEL + (a,), accent + (int(120 * p),), 2)
    d.text((x + 28, y + y_off + 22), title, font=F_TINY_B, fill=accent + (int(255 * p),))
    d.text((x + 28, y + y_off + 58), value, font=F_H2, fill=INK + (int(255 * p),))
    d.text((x + 28, y + y_off + 126), caption, font=F_TINY, fill=INK_SOFT + (int(235 * p),))


def draw_base_diamond(frame: Image.Image, center: tuple[int, int], scale: float, lit: int, p: float) -> None:
    d = ImageDraw.Draw(frame, "RGBA")
    cx, cy = center
    r = int(126 * scale)
    pts = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
    d.line(pts + [pts[0]], fill=WHITE + (185,), width=7)
    d.line(pts + [pts[0]], fill=INK + (75,), width=3)
    for i, (x, y) in enumerate(pts):
        color = ORANGE if i < lit else WHITE
        outline = ORANGE if i < lit else LINE
        s = int(25 * scale)
        d.rounded_rectangle((x - s, y - s, x + s, y + s), radius=max(4, int(6 * scale)), fill=color + (245,), outline=outline + (250,), width=3)
    d.text((cx - 72, cy - 18), "ON BASE", font=F_TINY_B, fill=INK + (220,))


def draw_field_path(frame: Image.Image, points: list[tuple[int, int]], p: float, accent=DIRT) -> None:
    d = ImageDraw.Draw(frame, "RGBA")
    if len(points) < 2:
        return
    visible = max(1, int((len(points) - 1) * clamp(p)))
    for idx in range(visible):
        x1, y1 = points[idx]
        x2, y2 = points[idx + 1]
        d.line((x1, y1, x2, y2), fill=accent + (165,), width=8)
        d.line((x1, y1, x2, y2), fill=WHITE + (130,), width=2)


def overlay_traffic(frame: Image.Image, p: float, _t_abs: float) -> None:
    d = ImageDraw.Draw(frame, "RGBA")
    draw_title_stack(frame, "比赛还没开打，意外先到场。", "冷开场", p)
    draw_chip(frame, (84, 594), "高速临时管制", clamp((p - 0.20) / 0.20), RED)
    draw_chip(frame, (84, 682), "集合时间 08:30", clamp((p - 0.34) / 0.20), ORANGE)
    draw_chip(frame, (84, 770), "两队都有队员被堵在路上", clamp((p - 0.48) / 0.22), BLUE)
    rounded(d, (76, 1014, 858, 1166), 26, PANEL + (220,), RED + (105,), 2)
    d.text((112, 1048), "开赛前 30 分钟", font=F_SMALL_B, fill=INK + (245,))
    d.text((112, 1102), "阵容的不确定性开始影响整个休息区。", font=F_TINY_B, fill=INK_SOFT + (235,))


def overlay_matchup(frame: Image.Image, p: float, _t_abs: float) -> None:
    d = ImageDraw.Draw(frame, "RGBA")
    d.text((72, 236), "08:30", font=F_DISPLAY, fill=NAVY + (255,))
    d.text((76, 338), "暑期杯训练赛", font=F_H2, fill=INK + (245,))
    y = 508
    rounded(d, (72, y, W - 72, y + 224), 30, PANEL + (230,), ORANGE + (128,), 3)
    d.text((112, y + 40), "北洲航海家", font=F_H1, fill=INK + (255,))
    d.text((116, y + 119), "BEIZHOU VOYAGER", font=F_SMALL_B, fill=NAVY + (238,))
    d.text((W - 230, y + 76), "VS", font=F_H1, fill=ORANGE + (255,))
    rounded(d, (72, y + 266, W - 72, y + 490), 30, PANEL + (230,), RED + (128,), 3)
    d.text((112, y + 306), "城南流星", font=F_H1, fill=INK + (255,))
    d.text((116, y + 385), "CHENGNAN METEORS", font=F_SMALL_B, fill=RED + (238,))
    draw_info_card(frame, (82, 1195), "7 号队长", "林澈", "CF / P 二刀流", clamp((p - 0.46) / 0.26), ORANGE, 420)
    draw_info_card(frame, (564, 1195), "训练赛", "上半局", "航海家先攻", clamp((p - 0.56) / 0.26), BLUE, 420)


def overlay_missing(frame: Image.Image, p: float, _t_abs: float) -> None:
    d = ImageDraw.Draw(frame, "RGBA")
    d.text((72, 246), "默认打线不能用了。", font=F_H1, fill=INK + (255,))
    d.text((76, 326), "主力未到场，替补要马上进入比赛。", font=F_SMALL_B, fill=NAVY + (235,))
    roster_y = 500
    names = ["三棒", "四棒", "外野", "替补", "投手", "游击"]
    for i, name in enumerate(names):
        x = 82 + (i % 3) * 310
        y = roster_y + (i // 3) * 162
        missing = i in (0, 1, 2)
        pp = clamp((p - 0.10 - i * 0.05) / 0.22)
        rounded(d, (x, y, x + 250, y + 116), 22, PANEL + (int(232 * pp),), (RED if missing else GREEN) + (int(125 * pp),), 2)
        d.text((x + 28, y + 24), name, font=F_SMALL_B, fill=INK + (int(245 * pp),))
        d.text((x + 28, y + 72), "未到场" if missing else "待命", font=F_TINY_B, fill=(RED if missing else GREEN) + (int(238 * pp),))
    draw_info_card(frame, (86, 930), "阵容变化", "缺席 x3", "即时重新评估", clamp((p - 0.42) / 0.24), RED, 420)
    draw_info_card(frame, (574, 930), "替补角色", "启动", "不靠感觉硬凑", clamp((p - 0.56) / 0.24), GREEN, 420)


def overlay_workbench(frame: Image.Image, p: float, _t_abs: float) -> None:
    d = ImageDraw.Draw(frame, "RGBA")
    rounded(d, (66, 202, 606, 422), 28, PANEL + (226,), ORANGE + (110,), 2)
    d.text((104, 238), "HomeRun 上场", font=F_H1, fill=INK + (250,))
    draw_wrapped(d, (108, 326), "沈指导先看真实记录，再帮主教练重排打序。", F_SMALL_B, NAVY + (235,), 450, 10)
    draw_product_panel(
        frame,
        "scorekeeping",
        (614, 206, 1018, 1136),
        clamp((p - 0.18) / 0.34),
        "专业计分",
        "场上站位 / 跑垒状态",
        GREEN,
    )
    draw_info_card(frame, (76, 1030), "决策原则", "证据优先", "不是谁像主力，而是谁能接住这一局", clamp((p - 0.42) / 0.28), ORANGE, 500)
    draw_chip(frame, (82, 1248), "阵容维护", clamp((p - 0.55) / 0.18), BLUE)
    draw_chip(frame, (312, 1248), "训练记录", clamp((p - 0.62) / 0.18), GREEN)
    draw_chip(frame, (542, 1248), "打席数据", clamp((p - 0.69) / 0.18), ORANGE)


def overlay_lineup(frame: Image.Image, p: float, _t_abs: float) -> None:
    d = ImageDraw.Draw(frame, "RGBA")
    d.text((72, 232), "点球成金式打线", font=F_H1, fill=INK + (255,))
    d.text((76, 314), "谁能让下一名队友前进，谁就是这局的答案。", font=F_SMALL_B, fill=NAVY + (235,))
    draw_product_panel(
        frame,
        "stats",
        (634, 418, 1010, 1228),
        clamp((p - 0.18) / 0.34),
        "数据分布",
        "落点与表现趋势",
        ORANGE,
    )
    cards = [
        ("苏晴", "提前", "选球上垒"),
        ("顾鸣", "二棒", "推进打稳定"),
        ("纪安安", "上场", "短打训练记录"),
        ("林澈", "关键位", "三游间地滚球"),
    ]
    for i, (name, val, cap) in enumerate(cards):
        x = 76 if i < 3 else 328
        y = 444 + i * 166 if i < 3 else 1086
        draw_info_card(frame, (x, y), name, val, cap, clamp((p - 0.14 - i * 0.09) / 0.24), [GREEN, BLUE, ORANGE, RED][i], 410 if i < 3 else 520)


def overlay_walk(frame: Image.Image, p: float, _t_abs: float) -> None:
    d = ImageDraw.Draw(frame, "RGBA")
    d.text((72, 238), "第一棒：先上垒", font=F_H1, fill=INK + (255,))
    draw_info_card(frame, (76, 374), "苏晴", "四坏球", "把压力交回给对手投手", clamp((p - 0.16) / 0.26), GREEN, 500)
    draw_product_panel(
        frame,
        "atbat",
        (652, 282, 1010, 1046),
        clamp((p - 0.30) / 0.34),
        "打席记录",
        "每一次选择都被留下",
        BLUE,
    )
    draw_base_diamond(frame, (302, 1042), 0.82, int(1 + 0.3 * p), p)
    draw_chip(frame, (86, 1264), "一垒有人", clamp((p - 0.55) / 0.2), GREEN)


def overlay_advance(frame: Image.Image, p: float, _t_abs: float) -> None:
    d = ImageDraw.Draw(frame, "RGBA")
    d.text((72, 236), "第二棒：推进", font=F_H1, fill=INK + (255,))
    d.text((76, 318), "顾鸣把球推向右半边，跑者稳稳前进。", font=F_SMALL_B, fill=NAVY + (235,))
    draw_field_path(frame, [(168, 1010), (288, 940), (420, 890), (548, 858)], clamp((p - 0.28) / 0.34), DIRT)
    draw_base_diamond(frame, (804, 1016), 0.90, 2, p)
    draw_info_card(frame, (84, 1176), "局面", "一出局二垒", "替补打线继续制造机会", clamp((p - 0.48) / 0.28), BLUE, 500)


def overlay_bunt(frame: Image.Image, p: float, _t_abs: float) -> None:
    d = ImageDraw.Draw(frame, "RGBA")
    d.text((72, 236), "第三棒：短打", font=F_H1, fill=INK + (255,))
    d.text((76, 318), "纪安安把球停在三垒线，满垒形成。", font=F_SMALL_B, fill=NAVY + (235,))
    draw_field_path(frame, [(142, 1068), (236, 1024), (330, 994), (430, 980)], clamp((p - 0.24) / 0.32), DIRT)
    draw_base_diamond(frame, (W // 2, 1104), 1.04, int(1 + 3 * clamp((p - 0.34) / 0.42)), p)
    if p > 0.72:
        sw, _ = text_size(d, "满垒", F_DISPLAY)
        rounded(d, (W // 2 - 174, 1300, W // 2 + 174, 1414), 30, ORANGE + (238,), None)
        d.text(((W - sw) // 2, 1296), "满垒", font=F_DISPLAY, fill=WHITE + (255,))


def overlay_gap(frame: Image.Image, p: float, _t_abs: float) -> None:
    d = ImageDraw.Draw(frame, "RGBA")
    rounded(d, (72, 218, 690, 396), 28, PANEL + (222,), BLUE + (100,), 2)
    d.text((112, 250), "守备弱点被看见", font=F_H1, fill=INK + (250,))
    d.text((116, 330), "三垒前压，游击补位慢半步", font=F_SMALL_B, fill=NAVY + (235,))
    draw_product_panel(
        frame,
        "stats",
        (712, 224, 1014, 884),
        clamp((p - 0.22) / 0.34),
        "落点趋势",
        "真实产品画面",
        ORANGE,
    )
    cx, cy = 430, 850
    field = [(cx - 210, cy + 160), (cx, cy - 120), (cx + 228, cy + 158)]
    d.line(field, fill=WHITE + (165,), width=8)
    d.line(field, fill=INK + (72,), width=3)
    d.line((cx - 205, cy + 130, cx + 244, cy - 108), fill=ORANGE + (175,), width=6)
    draw_chip(frame, (90, 1218), "林澈：打到最需要的位置", clamp((p - 0.52) / 0.2), ORANGE)


def overlay_grounder(frame: Image.Image, p: float, _t_abs: float) -> None:
    d = ImageDraw.Draw(frame, "RGBA")
    d.text((72, 222), "强袭地滚球", font=F_H1, fill=INK + (255,))
    d.text((76, 304), "白球贴着泥土穿过三游间，跑者接连回本垒。", font=F_SMALL_B, fill=NAVY + (235,))
    draw_field_path(frame, [(166, 1128), (300, 1064), (446, 1002), (604, 934), (774, 846)], clamp((p - 0.20) / 0.42), DIRT)
    score_steps = ["1 分", "2 分", "3 分", "林澈冲三垒"]
    for i, label in enumerate(score_steps):
        pp = clamp((p - 0.18 - i * 0.15) / 0.18)
        if pp > 0:
            x = 92 + (i % 2) * 438
            y = 1196 + (i // 2) * 102
            rounded(d, (x, y, x + 374, y + 72), 18, PANEL + (int(236 * pp),), ORANGE + (int(130 * pp),), 2)
            d.text((x + 28, y + 18), label, font=F_SMALL_B, fill=INK + (int(255 * pp),))


def overlay_slide(frame: Image.Image, p: float, _t_abs: float) -> None:
    d = ImageDraw.Draw(frame, "RGBA")
    d.text((72, 220), "场内本垒打", font=F_H1, fill=INK + (255,))
    sw, _ = text_size(d, "4 - 0", F_DISPLAY)
    rounded(d, (W // 2 - 246, 340, W // 2 + 246, 466), 32, ORANGE + (int(238 * clamp((p - 0.24) / 0.18)),), None)
    d.text(((W - sw) // 2, 342), "4 - 0", font=F_DISPLAY, fill=WHITE + (int(255 * clamp((p - 0.24) / 0.18)),))
    draw_product_panel(
        frame,
        "share",
        (700, 658, 1010, 1328),
        clamp((p - 0.42) / 0.30),
        "分享战报",
        "关键表现一键沉淀",
        GREEN,
    )
    if p > 0.54:
        rounded(d, (74, 1190, 648, 1338), 26, PANEL + (226,), ORANGE + (105,), 2)
        d.text((108, 1224), "一条打线，不只靠最强的人。", font=F_SMALL_B, fill=INK + (242,))
        d.text((108, 1276), "它靠每一个被看见的选择。", font=F_SMALL_B, fill=NAVY + (236,))


def overlay_late_arrival(frame: Image.Image, p: float, _t_abs: float) -> None:
    d = ImageDraw.Draw(frame, "RGBA")
    rounded(d, (72, 220, 700, 394), 28, PANEL + (226,), RED + (105,), 2)
    d.text((112, 254), "迟到队员赶到", font=F_H1, fill=INK + (250,))
    d.text((116, 332), "完整阵容回来了，比赛也变得更紧。", font=F_SMALL_B, fill=NAVY + (235,))
    draw_product_panel(
        frame,
        "live",
        (716, 210, 1016, 866),
        clamp((p - 0.24) / 0.34),
        "Live Console",
        "比赛状态同步",
        BLUE,
    )
    draw_info_card(frame, (80, 1044), "上半局", "4 分", "北洲航海家抢先", clamp((p - 0.32) / 0.24), ORANGE, 420)
    draw_info_card(frame, (568, 1044), "下半局", "反击", "城南流星进攻", clamp((p - 0.48) / 0.24), RED, 420)


def overlay_cliffhanger(frame: Image.Image, p: float, _t_abs: float) -> None:
    d = ImageDraw.Draw(frame, "RGBA")
    rounded(d, (74, 224, W - 74, 430), 30, PANEL + (226,), ORANGE + (105,), 2)
    d.text((112, 260), "下半局悬念", font=F_H1, fill=INK + (255,))
    d.text((116, 342), "航海家守得住，还是流星追回？", font=F_SMALL_B, fill=NAVY + (240,))
    draw_base_diamond(frame, (W // 2, 1020), 1.0, 0, p)
    draw_chip(frame, (118, 1248), "林澈准备防守", clamp((p - 0.26) / 0.24), NAVY)
    draw_chip(frame, (118, 1330), "赵燃准备反击", clamp((p - 0.42) / 0.24), RED)
    d.text((118, 1452), "期待第二集《反击》", font=F_H2, fill=INK + (245,))


def overlay_endcard(frame: Image.Image, p: float, _t_abs: float) -> None:
    d = ImageDraw.Draw(frame, "RGBA")
    overlay_tint(frame, WHITE, 34)
    rounded(d, (88, 214, W - 88, 506), 34, PANEL + (232,), ORANGE + (125,), 3)
    sw, _ = text_size(d, "HomeRun", F_DISPLAY)
    d.text(((W - sw) // 2, 270), "HomeRun", font=F_DISPLAY, fill=ORANGE + (255,))
    d.text((176, 382), "让棒球被热爱，让进步留脚印。", font=F_SMALL_B, fill=INK + (245,))
    labels = [
        ("专业计分", GREEN),
        ("阵容维护", BLUE),
        ("数据战报", ORANGE),
        ("AI 成长记录", RED),
    ]
    for i, (label, accent) in enumerate(labels):
        draw_chip(frame, (132 + (i % 2) * 420, 718 + (i // 2) * 96), label, clamp((p - 0.14 - i * 0.08) / 0.20), accent)
    d.text((176, 1184), "EPIC 002", font=F_H2, fill=NAVY + (235,))
    d.text((176, 1252), "反击", font=F_DISPLAY, fill=INK + (250,))
    d.text((180, 1366), "敬请期待", font=F_SMALL_B, fill=INK_SOFT + (235,))


OVERLAYS: dict[str, Callable[[Image.Image, float, float], None]] = {
    "traffic": overlay_traffic,
    "matchup": overlay_matchup,
    "missing": overlay_missing,
    "workbench": overlay_workbench,
    "lineup": overlay_lineup,
    "walk": overlay_walk,
    "advance": overlay_advance,
    "bunt": overlay_bunt,
    "gap": overlay_gap,
    "grounder": overlay_grounder,
    "slide": overlay_slide,
    "late_arrival": overlay_late_arrival,
    "cliffhanger": overlay_cliffhanger,
    "endcard": overlay_endcard,
}


SCENES: list[Scene] = [
    Scene("S01", 6.0, "S01", "有些比赛，还没开打，就先被意外投了一颗坏球。", "冷开场", "traffic", (0.38, 0.18), (0.58, 0.44), (255, 250, 238), 14),
    Scene("S02", 6.5, "S02", "暑期杯训练赛，北洲航海家对阵城南流星。集合时间，8 点 30 分。", "8:30 集合", "matchup", (0.54, 0.16), (0.44, 0.58), (245, 252, 255), 18),
    Scene("S03", 7.0, "S03", "高速临时管制，两队都有主力无法准时到场。默认打线失效。", "意外扩大", "missing", (0.40, 0.22), (0.58, 0.62), (255, 250, 245), 18),
    Scene("S04", 8.5, "S04", "沈指导打开 HomeRun：先别找谁像主力，先找谁能把这一局接起来。", "HomeRun 上场", "workbench", (0.42, 0.18), (0.54, 0.64), (248, 255, 248), 18),
    Scene("S05", 8.0, "S05", "不是赌，是用证据排。每一次训练记录，都会在临场决策里发挥作用。", "数据打线", "lineup", (0.36, 0.18), (0.58, 0.60), (251, 255, 248), 16),
    Scene("S06", 6.5, "S06", "苏晴选球上垒，先把比赛重新拉回可控的节奏。", "第一棒", "walk", (0.58, 0.22), (0.40, 0.58), (250, 255, 246), 14),
    Scene("S07", 6.5, "S07", "顾鸣轻推右半边，跑者稳稳前进。替补打线开始运转。", "推进", "advance", (0.35, 0.26), (0.62, 0.58), (251, 255, 248), 14),
    Scene("S08", 7.0, "S08", "纪安安短打沿三垒线滚动，把队友一个一个送到满垒。", "满垒", "bunt", (0.50, 0.22), (0.50, 0.62), (255, 252, 246), 14),
    Scene("S09", 8.0, "S09", "林澈看见三游间的空隙：不是打最远，而是打到比赛最需要的地方。", "队长打席", "gap", (0.52, 0.16), (0.40, 0.54), (247, 253, 255), 16),
    Scene("S10", 7.0, "S10", "强袭地滚球贴着泥土穿过防线，跑者连续回本垒。", "强袭地滚", "grounder", (0.30, 0.34), (0.70, 0.52), (255, 250, 242), 12),
    Scene("S11", 7.5, "S11", "林澈扑回本垒，场内本垒打。北洲航海家上半局带回 4 分。", "4 - 0", "slide", (0.46, 0.22), (0.52, 0.58), (255, 250, 244), 14),
    Scene("S12", 6.5, "S12", "迟到队员同时赶到。比赛没有结束，紧张才刚刚开始。", "局势升级", "late_arrival", (0.48, 0.18), (0.57, 0.60), (248, 252, 255), 16),
    Scene("S13", 8.0, "S13", "下半局，是航海家的防守更强，还是流星追回比赛？", "下半局悬念", "cliffhanger", (0.48, 0.16), (0.54, 0.56), (247, 253, 255), 14),
    Scene("END", 5.0, "cover", "让棒球被热爱，让进步留脚印。第二集《反击》，敬请期待。", "HomeRun", "endcard", (0.50, 0.18), (0.50, 0.54), WHITE, 24),
]

TOTAL_DURATION = sum(scene.duration for scene in SCENES)
SCENE_STARTS: dict[str, float] = {}
_cursor = 0.0
for _scene in SCENES:
    SCENE_STARTS[_scene.key] = _cursor
    _cursor += _scene.duration


def keyframe_paths(root: Path) -> dict[str, Path]:
    key_dir = root / "HomeRun/06_exports/job-003-anime-episode-001-production/keyframes/v0.2"
    return {
        "S01": key_dir / "S01_daytime_traffic_control.png",
        "S02": key_dir / "S02_daytime_830_field_arrival.png",
        "S03": key_dir / "S03_daytime_missing_players_dugout.png",
        "S04": key_dir / "S04_daytime_coach_tablet_blank.png",
        "S05": key_dir / "S05_daytime_lineup_decision.png",
        "S06": key_dir / "S06_daytime_suqing_walks_on_base.png",
        "S07": key_dir / "S07_daytime_guming_advances_runner.png",
        "S08": key_dir / "S08_daytime_bunt_bases_loaded.png",
        "S09": key_dir / "S09_daytime_linche_reads_gap.png",
        "S10": key_dir / "S10_daytime_real_ground_ball_gap.png",
        "S11": key_dir / "S11_daytime_linche_home_slide_real.png",
        "S12": key_dir / "S12_daytime_late_players_arrive.png",
        "S13": key_dir / "S13_daytime_defense_cliffhanger.png",
    }


def product_paths(root: Path) -> dict[str, Path]:
    product_dir = root / "HomeRun/05_working_files/job-003-anime-episode-001-production/source-assets/product-070"
    return {
        "scorekeeping": product_dir / "product-scorekeeping-field.png",
        "ai": product_dir / "product-ai-motion-analysis.png",
        "stats": product_dir / "product-stats-distribution.png",
        "atbat": product_dir / "product-atbat-records.png",
        "share": product_dir / "product-share-card.png",
        "live": product_dir / "product-live-console.png",
        "cover": product_dir / "product-social-cover.png",
    }


def load_backgrounds(root: Path) -> dict[str, Image.Image]:
    assets = keyframe_paths(root)
    assets["cover"] = product_paths(root)["cover"]
    missing = [str(path) for path in assets.values() if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing background assets:\n" + "\n".join(missing))
    zooms = {
        "S01": 1.12,
        "S02": 1.10,
        "S03": 1.10,
        "S04": 1.10,
        "S05": 1.10,
        "S09": 1.11,
        "S10": 1.13,
        "S11": 1.10,
        "cover": 1.05,
    }
    return {key: prepare_bg(path, zooms.get(key, 1.09)) for key, path in assets.items()}


def load_products(root: Path) -> None:
    global PRODUCTS
    paths = product_paths(root)
    missing = [str(path) for path in paths.values() if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing product screenshots:\n" + "\n".join(missing))
    PRODUCTS = {
        key: ImageOps.exif_transpose(Image.open(path)).convert("RGBA")
        for key, path in paths.items()
    }


def scene_at(t_abs: float) -> tuple[Scene, float, float]:
    cursor = 0.0
    for scene in SCENES:
        if t_abs < cursor + scene.duration:
            local = t_abs - cursor
            return scene, local, local / scene.duration
        cursor += scene.duration
    scene = SCENES[-1]
    return scene, scene.duration, 1.0


def score_at(t_abs: float) -> str:
    if t_abs >= SCENE_STARTS["S11"] + 1.8:
        return "4-0"
    if t_abs >= SCENE_STARTS["S10"] + 4.7:
        return "3-0"
    if t_abs >= SCENE_STARTS["S10"] + 3.4:
        return "2-0"
    if t_abs >= SCENE_STARTS["S10"] + 2.1:
        return "1-0"
    return "0-0"


def render_frame(backgrounds: dict[str, Image.Image], frame_idx: int) -> Image.Image:
    t_abs = frame_idx / FPS
    scene, local, p = scene_at(t_abs)
    frame = crop_pan(backgrounds[scene.bg], p, scene.start_pos, scene.end_pos).convert("RGBA")
    overlay_tint(frame, scene.wash, scene.wash_alpha)
    frame.alpha_composite(READABILITY)
    draw_top_bar(frame, t_abs, score_at(t_abs))
    OVERLAYS[scene.overlay](frame, p, t_abs)
    if scene.overlay != "endcard":
        draw_subtitle(frame, scene.subtitle, scene.title)
    fade = 0.0
    if local < 0.28:
        fade = max(fade, 1 - local / 0.28)
    if scene.duration - local < 0.28:
        fade = max(fade, 1 - (scene.duration - local) / 0.28)
    if fade:
        overlay_tint(frame, WHITE, int(130 * fade))
    return frame.convert("RGB")


def write_audio(path: Path, duration: float) -> None:
    n = int(duration * SR)
    t = np.arange(n, dtype=np.float32) / SR
    rng = np.random.default_rng(20260706)
    mix = np.zeros(n, dtype=np.float32)

    # Bright sports-promo bed: field ambience, light pulse, and restrained hits.
    mix += 0.025 * np.sin(math.tau * 74 * t) * (0.55 + 0.45 * np.sin(math.tau * 0.10 * t))
    mix += 0.013 * np.sin(math.tau * 148 * t + 0.3 * np.sin(math.tau * 0.18 * t))
    noise = rng.normal(0, 1, n).astype(np.float32)
    kernel = np.ones(420, dtype=np.float32) / 420
    crowd = np.convolve(noise, kernel, mode="same")
    crowd /= max(0.001, float(np.max(np.abs(crowd))))
    mix += 0.026 * crowd

    def add_segment(start: float, signal: np.ndarray, amp: float = 1.0) -> None:
        i0 = max(0, int(start * SR))
        i1 = min(n, i0 + len(signal))
        if i1 > i0:
            mix[i0:i1] += amp * signal[: i1 - i0]

    def kick(start: float, amp: float = 0.45) -> None:
        dur = 0.30
        m = int(dur * SR)
        u = np.linspace(0, 1, m, endpoint=False, dtype=np.float32)
        freq = 88 - 45 * u
        phase = math.tau * np.cumsum(freq) / SR
        sig = np.sin(phase) * np.exp(-8.0 * u)
        add_segment(start, sig.astype(np.float32), amp)

    def tick(start: float, amp: float = 0.14) -> None:
        dur = 0.052
        m = int(dur * SR)
        u = np.linspace(0, 1, m, endpoint=False, dtype=np.float32)
        sig = rng.normal(0, 1, m).astype(np.float32) * np.exp(-42 * u)
        add_segment(start, sig, amp)

    def whoosh(start: float, dur: float = 0.72, amp: float = 0.16) -> None:
        m = int(dur * SR)
        u = np.linspace(0, 1, m, endpoint=False, dtype=np.float32)
        sig = rng.normal(0, 1, m).astype(np.float32)
        env = np.sin(np.pi * u) ** 1.8
        tone = np.sin(math.tau * (350 + 620 * u) * u * dur)
        add_segment(start, (0.72 * sig + 0.28 * tone).astype(np.float32) * env, amp)

    def hit(start: float, amp: float = 0.7) -> None:
        kick(start, amp * 0.90)
        m = int(0.16 * SR)
        u = np.linspace(0, 1, m, endpoint=False, dtype=np.float32)
        sig = rng.normal(0, 1, m).astype(np.float32) * np.exp(-22 * u)
        add_segment(start, sig, amp * 0.26)

    beat = 0.72
    current = 0.25
    while current < duration - 0.4:
        kick(current, 0.20 if current < SCENE_STARTS["S09"] else 0.28)
        tick(current + beat * 0.5, 0.08)
        current += beat

    for start in list(SCENE_STARTS.values())[1:]:
        whoosh(start - 0.18, 0.56, 0.14)

    for s in [
        SCENE_STARTS["S06"] + 2.2,
        SCENE_STARTS["S07"] + 2.7,
        SCENE_STARTS["S08"] + 3.2,
        SCENE_STARTS["S10"] + 2.2,
        SCENE_STARTS["S10"] + 3.6,
        SCENE_STARTS["S10"] + 5.0,
        SCENE_STARTS["S11"] + 2.0,
        SCENE_STARTS["S12"] + 1.4,
    ]:
        tick(s, 0.20)
    hit(SCENE_STARTS["S10"] + 1.2, 0.72)
    whoosh(SCENE_STARTS["S10"] + 1.6, 1.05, 0.18)
    hit(SCENE_STARTS["S11"] + 2.0, 0.72)

    finale_start = int(SCENE_STARTS["END"] * SR)
    if finale_start < n:
        u = np.linspace(0, 1, n - finale_start, endpoint=False, dtype=np.float32)
        lift = 0.035 * np.sin(math.tau * (176 + 14 * u) * u * (duration - SCENE_STARTS["END"])) * (u ** 0.6)
        mix[finale_start:] += lift.astype(np.float32)

    mx = max(0.001, float(np.max(np.abs(mix))))
    mix = (mix / mx * 0.82).astype(np.float32)
    stereo = np.stack([mix, mix * 0.97], axis=1)
    pcm = np.clip(stereo * 32767, -32768, 32767).astype("<i2")
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(SR)
        wav.writeframes(pcm.tobytes())


def write_scene_manifest(path: Path) -> None:
    cursor = 0.0
    data = []
    for scene in SCENES:
        data.append(
            {
                "shot_id": scene.key,
                "start": round(cursor, 3),
                "end": round(cursor + scene.duration, 3),
                "duration": scene.duration,
                "title": scene.title,
                "subtitle": scene.subtitle,
                "background": scene.bg,
                "overlay": scene.overlay,
                "visual_direction": "v0.2 daylight realistic baseball, no fireball or fantasy effects",
            }
        )
        cursor += scene.duration
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def encode_video(backgrounds: dict[str, Image.Image], audio_path: Path, output_path: Path, preset: str = "medium") -> None:
    if not FFMPEG.exists():
        raise FileNotFoundError(f"ffmpeg not found at {FFMPEG}")
    total_frames = int(math.ceil(TOTAL_DURATION * FPS))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    log_path = output_path.with_suffix(".ffmpeg.log")
    cmd = [
        str(FFMPEG),
        "-y",
        "-f",
        "rawvideo",
        "-pix_fmt",
        "rgb24",
        "-s",
        f"{W}x{H}",
        "-r",
        str(FPS),
        "-i",
        "-",
        "-i",
        str(audio_path),
        "-c:v",
        "libx264",
        "-preset",
        preset,
        "-crf",
        "20",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "160k",
        "-shortest",
        "-movflags",
        "faststart",
        str(output_path),
    ]
    with log_path.open("wb") as log:
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=log, stderr=log)
        assert proc.stdin is not None
        try:
            for idx in range(total_frames):
                frame = render_frame(backgrounds, idx)
                proc.stdin.write(np.asarray(frame, dtype=np.uint8).tobytes())
                if idx and idx % (FPS * 10) == 0:
                    print(f"rendered {idx // FPS:>3}s / {TOTAL_DURATION:.0f}s", flush=True)
        except BrokenPipeError as exc:
            raise RuntimeError(f"ffmpeg closed the pipe early; see {log_path}") from exc
        finally:
            proc.stdin.close()
        code = proc.wait()
    if code != 0:
        tail = log_path.read_text(errors="ignore")[-4000:]
        raise RuntimeError(f"ffmpeg failed with code {code}; tail:\n{tail}")


def export_preview_frames(backgrounds: dict[str, Image.Image], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    stamps = {
        "preview_01_daytime_opening.png": 2.6,
        "preview_02_homerun_real_product.png": SCENE_STARTS["S04"] + 3.8,
        "preview_03_lineup_decision.png": SCENE_STARTS["S05"] + 4.0,
        "preview_04_bases_loaded.png": SCENE_STARTS["S08"] + 5.2,
        "preview_05_ground_ball_real.png": SCENE_STARTS["S10"] + 4.8,
        "preview_06_home_slide_score.png": SCENE_STARTS["S11"] + 3.3,
        "preview_07_late_arrival_live.png": SCENE_STARTS["S12"] + 3.6,
        "preview_08_cliffhanger.png": SCENE_STARTS["S13"] + 5.0,
    }
    for name, seconds in stamps.items():
        render_frame(backgrounds, int(seconds * FPS)).save(out_dir / name)


def probe_video(path: Path) -> str:
    if not FFPROBE.exists():
        return "ffprobe unavailable"
    cmd = [
        str(FFPROBE),
        "-v",
        "error",
        "-show_entries",
        "format=duration:stream=codec_type,width,height,codec_name",
        "-of",
        "json",
        str(path),
    ]
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    return result.stdout


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preset", default="medium", help="x264 preset; use ultrafast for quick test renders")
    args = parser.parse_args()

    root = repo_root()
    dirs = out_dirs(root)
    for path in dirs.values():
        path.mkdir(parents=True, exist_ok=True)

    output = dirs["videos"] / "homerun-epic-001-accident-v0.2.mp4"
    audio = dirs["audio"] / "homerun-epic-001-v0.2-synthetic-mix.wav"
    manifest = dirs["work"] / "scripts/episode-001-scene-manifest-v0.2.json"
    probe = dirs["work"] / "progress/episode-001-v0.2-ffprobe.json"

    print("loading backgrounds", flush=True)
    backgrounds = load_backgrounds(root)
    print("loading real product screenshots", flush=True)
    load_products(root)
    print("writing audio", flush=True)
    write_audio(audio, TOTAL_DURATION)
    print("writing scene manifest", flush=True)
    write_scene_manifest(manifest)
    print("encoding video", flush=True)
    encode_video(backgrounds, audio, output, preset=args.preset)
    print("exporting preview frames", flush=True)
    export_preview_frames(backgrounds, dirs["scenes"])
    probe.write_text(probe_video(output), encoding="utf-8")
    print(f"done: {output}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
