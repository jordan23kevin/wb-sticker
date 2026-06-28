"""核心 — 正图贴图（尾数2，直写03_UPLOAD）"""

import os
import time
import ctypes

from config.settings import BTN, BASE_TORSO, SOURCE_BASE, MIN_FILE_SIZE
from services.win32 import ff, click, drag, key_comb, mdown, mmove, mup
from services.meitu import (
    find_meitu, launch_meitu, switch_torso, enter_ai_sticker,
    wait_sticker, import_file, do_mix, save_image,
)
u = ctypes.windll.user32


def process_front(dx_folder: str, png_name: str, is_black: bool = False, skip_ai_entry: bool = False) -> bool:
    """处理正图贴图，直接输出到 03_UPLOAD"""
    color_label = "黑T" if is_black else "白T"
    color_output = "黑T" if is_black else "白T"
    torso_name = "黑正2.jpg" if is_black else "白正2.jpg"
    torso_path = os.path.join(BASE_TORSO, torso_name)

    png_path = os.path.join(SOURCE_BASE, dx_folder, "02_REM_BG", png_name)
    output_name = f"{dx_folder}_W_{color_output}.jpg"
    output_path = os.path.join(SOURCE_BASE, dx_folder, "03_UPLOAD", output_name)

    print(f"{color_label} 正 — {dx_folder}/{png_name}", flush=True)

    if os.path.exists(output_path) and os.path.getsize(output_path) > MIN_FILE_SIZE:
        print("  [OK] 已存在，跳过", flush=True)
        return True

    hwnd = find_meitu()
    if skip_ai_entry and hwnd:
        # 美图已打开好胚衣+AI贴图，直接开始
        ff(hwnd)
        time.sleep(0.2)
    elif hwnd:
        hwnd = switch_torso(hwnd, torso_path, keep_alive=True)
        if not hwnd:
            return False
        time.sleep(1.5)
        # 复用美图不点AI入口，直接点新增图片
    else:
        hwnd = launch_meitu(torso_path)
        if not hwnd:
            return False
        time.sleep(0.2)
        enter_ai_sticker(hwnd)

    ff(hwnd)
    time.sleep(0.2)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    click(*BTN["add_image"], 0.5)
    if not import_file(png_path):
        print("  [FAIL] 首次失败，展开AI面板重试...", flush=True)
        u.keybd_event(0x1B, 0, 0, 0)
        time.sleep(0.02)
        u.keybd_event(0x1B, 0, 2, 0)
        time.sleep(0.2)
        enter_ai_sticker(hwnd)
        click(*BTN["add_image"], 0.5)
        if not import_file(png_path):
            return False

    ff(hwnd)
    wait_sticker(hwnd=hwnd)
    click(*BTN["sel_sticker"], 0.08)

    ff(hwnd)
    time.sleep(0.1)
    rx, ry = BTN["rotate_btn"]
    mdown(rx, ry)
    for s in range(3):
        mmove(rx + s + 1, ry)
        time.sleep(0.005)
    mup(0.08)
    time.sleep(0.2)
    click(*BTN["sel_sticker"], 0.08)

    ff(hwnd)
    drag((1906, 973), (2166, 705))

    do_mix(is_black)

    return save_image(hwnd, os.path.dirname(output_path), output_path)
