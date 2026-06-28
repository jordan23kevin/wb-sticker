"""流程编排 — WB贴图流水线（直读02_REM_BG，直写03_UPLOAD）"""

import os

from config.settings import SOURCE_BASE
from core.back import process_back
from core.front import process_front
from utils.sticker_typer import get_type
from utils.detector import is_dark_image


def run_pipeline(is_black: bool = False, single_folder: str | None = None, skip_ai_entry: bool = False):
    color_name = "黑T" if is_black else "白T"
    print("=" * 50)
    print(f"  WB贴图 v3.0 (OS) - {color_name}")
    print("=" * 50)
    print()

    if single_folder:
        folders = [single_folder]
    else:
        folders = sorted([
            d for d in os.listdir(SOURCE_BASE)
            if os.path.isdir(os.path.join(SOURCE_BASE, d)) and d.startswith("DX")
        ])

    print(f"待处理: {len(folders)} 个文件夹")
    for f in folders:
        print(f"  {f}")
    print()

    for dn in folders:
        rembg_dir = os.path.join(SOURCE_BASE, dn, "02_REM_BG")
        if not os.path.isdir(rembg_dir):
            continue
        pngs = sorted([f for f in os.listdir(rembg_dir) if f.lower().endswith(".png")])
        if not pngs:
            print(f"\n  [?] {dn}: 02_REM_BG 无文件")
            continue

        # 黑T：预检所有PNG，一张过暗则整组跳过
        if is_black:
            skip_all = False
            for png in pngs:
                if is_dark_image(os.path.join(rembg_dir, png)):
                    print(f"\n  [SKIP] {dn}: {png} 过暗，整组跳过黑T")
                    skip_all = True
                    break
            if skip_all:
                continue

        for png in pngs:
            t = get_type(png)
            if t == "front":
                print(f"\n{'=' * 40}\n  {dn}/{png} -> 正")
                if not process_front(dn, png, is_black, skip_ai_entry):
                    print("  [FAIL] 正处理失败")
            elif t == "back":
                print(f"\n{'=' * 40}\n  {dn}/{png} -> 背")
                if not process_back(dn, png, is_black, skip_ai_entry):
                    print("  [FAIL] 背处理失败")
            elif t == "both":
                print(f"\n{'=' * 40}\n  {dn}/{png} -> 背(1/2)")
                ok = process_back(dn, png, is_black, skip_ai_entry)
                if ok:
                    print(f"\n{'=' * 40}\n  {dn}/{png} -> 正(2/2)")
                    if not process_front(dn, png, is_black, skip_ai_entry):
                        print("  [FAIL] 正处理失败")
                else:
                    print("  [FAIL] 背处理失败，跳过正")
            else:
                print(f"\n  [?] 跳过 {dn}/{png} - 文件名不含B/W")
