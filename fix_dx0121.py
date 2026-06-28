"""
fix_dx0121.py — 单图修复 DX0121_W（用 Ctrl+O 绕过 add_image 按钮）
"""
import sys, os, time, ctypes, subprocess
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import MEITU_EXE, BASE_TORSO, SOURCE_BASE, BTN, MIN_FILE_SIZE, TAIL1
from services.meitu import find_meitu, launch_meitu, enter_ai_sticker, import_file, do_mix, save_image, wait_sticker, sample_pixels
from services.win32 import u, ff, click, mdown, mmove, mup, key_comb, drag

DX = "DX0121"
png_path = Path(SOURCE_BASE) / DX / "02_REM_BG" / "DX0121_BW_cut.png"
torso_path = Path(BASE_TORSO) / "白正2.jpg"
output_path = Path(SOURCE_BASE) / DX / "03_UPLOAD" / f"{DX}_W_白T.jpg"

if output_path.exists() and output_path.stat().st_size > 50000:
    print(f"[OK] {DX}_W_白T.jpg 已存在")
    sys.exit(0)

print(f"处理 {DX}_W ...")

# 杀旧进程开美图
subprocess.run(["taskkill", "/f", "/im", "XiuXiu.exe"], capture_output=True)
time.sleep(0.5)
subprocess.Popen([MEITU_EXE, str(torso_path)])

hwnd = None
for _ in range(30):
    time.sleep(0.2)
    hwnd = find_meitu()
    if hwnd: break

if not hwnd:
    print("[FAIL] 找不到美图窗口")
    sys.exit(1)

u.ShowWindow(hwnd, 9)
time.sleep(0.2)
u.SetWindowPos(hwnd, 0, 1280, 0, 1280, u.GetSystemMetrics(1), 0x0040)
u.SetForegroundWindow(hwnd)
time.sleep(2)  # 等T恤加载完

# 进AI贴图模式
enter_ai_sticker(hwnd)
time.sleep(0.5)

# Ctrl+O 打开文件（不用 add_image 按钮）
ff(hwnd)
time.sleep(0.1)
key_comb(0x11, 0x4F)
time.sleep(0.3)

if not import_file(str(png_path)):
    print("[FAIL] import_file failed")
    sys.exit(1)

# 贴图操作
ff(hwnd)
time.sleep(0.2)
before = sample_pixels()
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
drag((1906, 973), (2166, 705))

do_mix(False)

output_path.parent.mkdir(parents=True, exist_ok=True)
ok = save_image(hwnd, str(output_path.parent), str(output_path))

time.sleep(1)

if output_path.exists() and output_path.stat().st_size > 50000:
    print(f"[OK] {output_path.name} ({output_path.stat().st_size//1024}KB)")
else:
    # 检查默认名文件
    for f in output_path.parent.glob("*副本*"):
        print(f"[OK] 找到默认名: {f.name} ({f.stat().st_size//1024}KB)")
        import shutil
        shutil.move(str(f), str(output_path))
        print(f"  改名 -> {output_path.name}")
        sys.exit(0)

print(f"[结果] {'成功' if ok else '失败'}")
