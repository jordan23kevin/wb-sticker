"""核心 — 背图贴图（尾数1，直写03_UPLOAD）"""

import os
import time
import ctypes

from config.settings import MEITU_EXE, BTN, TAIL1, BASE_TORSO, SOURCE_BASE, MIN_FILE_SIZE
from services.win32 import ff, click, drag, key_comb, mdown, mmove, mup
from services.meitu import (
    find_meitu, launch_meitu, switch_torso, enter_ai_sticker,
    sample_pixels, wait_sticker, import_file, do_mix, save_image,
)
from utils.detector import calc_offset_back, is_dark_image

u = ctypes.windll.user32


def process_back(dx_folder: str, png_name: str, is_black: bool = False) -> bool:
    """处理背图贴图，直接输出到 03_UPLOAD"""
    color_label = "黑T" if is_black else "白T"
    color_output = "黑T" if is_black else "白T"
    torso_name = "黑背2.jpg" if is_black else "白背2.jpg"
    torso_path = os.path.join(BASE_TORSO, torso_name)

    png_path = os.path.join(SOURCE_BASE, dx_folder, "02_REM_BG", png_name)
    output_name = f"{dx_folder}_B_{color_output}.jpg"
    output_path = os.path.join(SOURCE_BASE, dx_folder, "03_UPLOAD", output_name)

    print(f"{color_label} 背 — {dx_folder}/{png_name}", flush=True)

    if os.path.exists(output_path) and os.path.getsize(output_path) > MIN_FILE_SIZE:
        print("  [OK] 已存在，跳过", flush=True)
        return True

    if is_black and is_dark_image(png_path):
        print("  [SKIP] 深色贴图，黑T跳过", flush=True)
        return True

    tx, ty = TAIL1["TARGET_X"], TAIL1["TARGET_Y"]
    dx, dy = calc_offset_back(png_path, tx, ty)
    print(f"  TARGET_X={tx}, dx={dx}, dy={dy}", flush=True)
    drag_start = TAIL1["DRAG_START"]

    hwnd = find_meitu()
    if not hwnd:
        hwnd = launch_meitu(torso_path)
        if not hwnd:
            return False
        time.sleep(0.2)
        enter_ai_sticker(hwnd)
    else:
        hwnd = switch_torso(hwnd, torso_path)
        if not hwnd:
            return False

    ff(hwnd)
    time.sleep(0.2)
    before = sample_pixels()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    click(*BTN["add_image"], 0.5)
    if not import_file(png_path):
        print("  [FAIL] 首次失败，重试...", flush=True)
        u.keybd_event(0x1B, 0, 0, 0)
        time.sleep(0.02)
        u.keybd_event(0x1B, 0, 2, 0)
        time.sleep(0.2)
        click(*BTN["add_image"], 0.5)
        if not import_file(png_path):
            print("  [FAIL] import_file failed", flush=True)
            return False

    ff(hwnd)
    wait_sticker(before)
    click(*BTN["sel_sticker"], 0.08)

    ff(hwnd)
    time.sleep(0.1)
    rx, ry = BTN["rotate_btn"]
    mdown(rx, ry)
    for s in range(2):
        mmove(rx + s + 1, ry)
        time.sleep(0.002)
    mup(0.08)
    time.sleep(0.1)
    click(*BTN["sel_sticker"], 0.08)

    ff(hwnd)
    sx, sy = drag_start
    drag((sx, sy), (sx + dx, sy + dy))

    do_mix(is_black)

    return save_image(hwnd, os.path.dirname(output_path), output_path)
