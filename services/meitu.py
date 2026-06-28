"""美图秀秀服务层 — 窗口管理、图片导入、保存"""

import ctypes
import os
import subprocess
import time
from ctypes import wintypes

from config.settings import MEITU_EXE, BTN
from services.win32 import u, ff, click, mdown, mmove, mup, key_comb, get_pixel


def find_meitu():
    """查找美图秀秀窗口句柄"""
    hwnd = u.FindWindowW(None, "美图秀秀-图片编辑")
    if hwnd:
        return hwnd

    _hw = [None]

    def ecb(h, l):
        b = ctypes.create_unicode_buffer(256)
        u.GetWindowTextW(h, b, 256)
        if '美图' in b.value or '秀秀' in b.value:
            _hw[0] = h
            return False
        return True

    u.EnumWindows(
        ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)(ecb), 0
    )
    return _hw[0]


def launch_meitu(torso_path):
    """启动美图秀秀打开胚衣（先杀旧进程）"""
    import os as _os, subprocess as _sp
    _os.system('taskkill /f /im XiuXiu.exe >nul 2>&1')
    time.sleep(0.2)
    _sp.Popen([MEITU_EXE, torso_path])
    # 等窗口出现，最多 10s
    hwnd = None
    for _ in range(20):
        time.sleep(0.2)
        hwnd = find_meitu()
        if hwnd:
            break
    if hwnd:
        u.ShowWindow(hwnd, 9)  # SW_RESTORE
        time.sleep(0.2)
        u.SetWindowPos(hwnd, 0, 1280, 0, 1280, u.GetSystemMetrics(1), 0x0040)
        u.SetForegroundWindow(hwnd)
        time.sleep(0.2)
    return hwnd


def switch_torso(hwnd, torso_path):
    """在已打开的美图中切换胚衣（不重启美图）"""
    ff(hwnd)
    key_comb(0x11, 0x57)  # Ctrl+W close
    time.sleep(0.1)
    u.keybd_event(0x0D, 0, 0, 0)  # Enter (confirm no save)
    time.sleep(0.02)
    u.keybd_event(0x0D, 0, 2, 0)
    time.sleep(0.2)
    # 直接打开新胚衣（不杀进程）
    subprocess.Popen([MEITU_EXE, torso_path])
    time.sleep(0.2)
    return hwnd


def enter_ai_sticker(hwnd):
    """进入AI贴图模式"""
    ff(hwnd)
    click(*BTN["AI_tools"], 1.0)
    click(*BTN["AI_sticker"], 1.0)


def sample_pixels(center_x=1920, center_y=700):
    """采样画布区域的像素值（贴图会出现的位置）"""
    # 画布中心区域 5x5 网格，覆盖 800x800 范围
    offsets = []
    for dx in range(-400, 401, 200):
        for dy in range(-400, 401, 200):
            offsets.append((dx, dy))
    return [get_pixel(center_x + dx, center_y + dy) for dx, dy in offsets]


def wait_sticker(before=None, center_x=0, center_y=0, timeout=0):
    """贴图置入后固定等 0.3s 渲染，然后继续"""
    time.sleep(0.2)
    return True


def import_file(png_path):
    """打开文件对话框 → 粘贴路径 → 导入"""
    dlg = None
    for _ in range(30):
        def fh(h, l):
            nonlocal dlg
            cls = ctypes.create_unicode_buffer(64)
            u.GetClassNameW(h, cls, 64)
            if cls.value == "#32770" and u.IsWindowVisible(h):
                dlg = h
                return False
            return True

        u.EnumWindows(
            ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)(fh),
            0,
        )
        if dlg:
            break
        time.sleep(0.1)
    if not dlg:
        print("  [FAIL] file dialog not found")
        return False

    ff(dlg)
    import pyperclip as _pc

    _pc.copy(png_path)
    time.sleep(0.05)
    key_comb(0x11, 0x41)  # Ctrl+A
    time.sleep(0.05)
    u.keybd_event(0x2E, 0, 0, 0)  # Del
    time.sleep(0.02)
    u.keybd_event(0x2E, 0, 2, 0)
    time.sleep(0.05)
    key_comb(0x11, 0x56)  # Ctrl+V
    time.sleep(0.1)
    u.keybd_event(0x0D, 0, 0, 0)  # Enter
    time.sleep(0.02)
    u.keybd_event(0x0D, 0, 2, 0)
    time.sleep(0.2)  # 等对话框关闭
    return True


def do_mix(is_black):
    """混合模式：白T三步，黑T两步"""
    if is_black:
        click(*BTN["black_mix"], 0.3)
        time.sleep(0.2)
        click(*BTN["black_normal"], 0.15)
    else:
        click(*BTN["mix_norm"], 0.05)
        click(*BTN["mix_sel"], 0.05)
        click(*BTN["mix_cfm"], 0.05)


def save_image(hwnd, folder_path, output_path):
    """保存图片到目标路径"""
    if os.path.exists(output_path):
        os.remove(output_path)

    ff(hwnd)
    key_comb(0x11, 0x53)  # Ctrl+S

    # 找到保存对话框
    sv = None

    def fsv(h, l):
        nonlocal sv
        cls = ctypes.create_unicode_buffer(64)
        u.GetClassNameW(h, cls, 64)
        if u.IsWindowVisible(h) and "ToolSa" in cls.value:
            sv = h
            return False
        return True

    for _ in range(5):
        u.EnumWindows(
            ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)(fsv),
            0,
        )
        if sv:
            break
        time.sleep(0.1)
    if not sv:
        print("  [FAIL] save dialog not found")
        return False

    # 设置保存路径
    ff(sv)
    import pyperclip as _pc

    for _c in range(2):
        u.SetCursorPos(2200, 555)
        time.sleep(0.02)
        u.mouse_event(0x0002, 0, 0, 0, 0)
        time.sleep(0.05)
        u.mouse_event(0x0004, 0, 0, 0, 0)
        time.sleep(0.05)
    time.sleep(0.1)
    key_comb(0x11, 0x41)
    time.sleep(0.02)
    key_comb(0x11, 0x43)
    time.sleep(0.03)

    u.keybd_event(0x2E, 0, 0, 0)
    time.sleep(0.02)
    u.keybd_event(0x2E, 0, 2, 0)
    time.sleep(0.02)
    _pc.copy(folder_path)
    time.sleep(0.05)
    key_comb(0x11, 0x56)
    time.sleep(0.1)

    # 设置质量为100
    ff(sv)
    click(*BTN["save_qual"], 0.1)
    time.sleep(0.1)
    key_comb(0x11, 0x41)
    time.sleep(0.05)
    u.keybd_event(0x2E, 0, 0, 0)
    time.sleep(0.02)
    u.keybd_event(0x2E, 0, 2, 0)
    time.sleep(0.02)
    _pc.copy("100")
    time.sleep(0.05)
    key_comb(0x11, 0x56)
    time.sleep(0.1)

    ff(sv)
    click(*BTN["save_btn"], 0.1)

    folder_contents = set(os.listdir(folder_path)) if os.path.isdir(folder_path) else set()
    for _ in range(15):  # 3s wait
        if os.path.exists(output_path) and os.path.getsize(output_path) > 50 * 1024:
            sz = os.path.getsize(output_path) // 1024
            print(f" [OK] {sz}KB", flush=True)
            return True
        for _alt in os.listdir(folder_path) if os.path.isdir(folder_path) else []:
            if _alt.endswith(".jpg") and _alt not in folder_contents:
                _ap = os.path.join(folder_path, _alt)
                if os.path.getsize(_ap) > 50 * 1024:
                    if os.path.exists(output_path):
                        os.remove(output_path)
                    os.rename(_ap, output_path)
                    sz = os.path.getsize(output_path) // 1024
                    print(f" [OK] {sz}KB", flush=True)
                    return True
        time.sleep(0.2)
    return False
