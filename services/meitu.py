"""美图秀秀服务层 — 窗口管理、图片导入、保存"""

import ctypes
import os
import subprocess
import time
from ctypes import wintypes

from config.settings import MEITU_EXE, BTN
from services.win32 import u, ff, click, mdown, mmove, mup, key_comb, get_pixel

# 美图窗口标题（繁体/简体）
_MEITU_TITLES = ("美圖秀秀", "美图秀秀")
# AI贴图面板状态（复用美图时跳过AI工具/AI贴图点击）
_ai_panel_open = False


def _has_title(b):
    """检查窗口标题是否包含美图秀秀（兼容繁简体）"""
    v = b.value
    return any(t in v for t in _MEITU_TITLES)


def find_meitu():
    """查找美图秀秀窗口句柄（繁简体兼容）"""
    # 先精确匹配繁简体两种可能
    for title in ("美圖秀秀-圖片編輯", "美图秀秀-图片编辑"):
        hwnd = u.FindWindowW(None, title)
        if hwnd:
            return hwnd

    # EnumWindows 模糊匹配
    _hw = [None]

    def ecb(h, l):
        b = ctypes.create_unicode_buffer(256)
        u.GetWindowTextW(h, b, 256)
        if _has_title(b):
            _hw[0] = h
            return False
        return True

    u.EnumWindows(
        ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)(ecb), 0
    )
    return _hw[0]


def launch_meitu(torso_path=None):
    """启动图片编辑 → 定位窗口 → 一步到位（直接打开胚衣）"""
    import os as _os, subprocess as _sp
    _os.system('taskkill /f /im XiuXiu.exe >nul 2>&1')
    time.sleep(0.3)

    # 一步：直接打开胚衣
    cmd = [MEITU_EXE]
    if torso_path:
        cmd.append(torso_path)
    _sp.Popen(cmd)

    hwnd = None
    for _ in range(40):
        time.sleep(0.3)
        def fh(h, l):
            nonlocal hwnd
            b = ctypes.create_unicode_buffer(64)
            u.GetWindowTextW(h, b, 64)
            if _has_title(b) and ('編輯' in b.value or '编辑' in b.value):
                hwnd = h
                return False
            return True
        u.EnumWindows(
            ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)(fh), 0
        )
        if hwnd:
            break

    if not hwnd:
        # 兜底：找任何美图窗口
        hwnd = find_meitu()

    if hwnd:
        u.ShowWindow(hwnd, 9)
        time.sleep(0.2)
        u.SetWindowPos(hwnd, 0, 1280, 0, 1280, u.GetSystemMetrics(1), 0x0040)
        u.SetForegroundWindow(hwnd)
        time.sleep(0.5)

    return hwnd


def switch_torso(hwnd, torso_path, keep_alive=False):
    """切换胚衣：
       keep_alive=False（默认）：杀进程重开（旧行为）
       keep_alive=True：关闭当前图+打开新胚衣，不杀进程
    """
    reset_ai_panel()  # 切胚衣后AI面板复位
    ff(hwnd)
    key_comb(0x11, 0x57)  # Ctrl+W close
    time.sleep(0.1)
    u.keybd_event(0x0D, 0, 0, 0)  # Enter (confirm no save)
    time.sleep(0.02)
    u.keybd_event(0x0D, 0, 2, 0)
    time.sleep(0.3)

    if keep_alive:
        # 不杀进程：用 Popen 打开新胚衣，美图会在当前窗口加载
        subprocess.Popen([MEITU_EXE, torso_path])
        for _ in range(60):  # 最多 12s
            time.sleep(0.2)
            # EnumWindows 找美图窗口（繁简体兼容）
            def fm(h, l):
                nonlocal hwnd
                b = ctypes.create_unicode_buffer(64)
                u.GetWindowTextW(h, b, 64)
                if _has_title(b):
                    hwnd = h
                    return False
                return True
            u.EnumWindows(
                ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)(fm), 0
            )
            if hwnd:
                u.ShowWindow(hwnd, 9)
                time.sleep(0.2)
                u.SetWindowPos(hwnd, 0, 1280, 0, 1280, u.GetSystemMetrics(1), 0x0040)
                u.SetForegroundWindow(hwnd)
                time.sleep(0.5)
                kill_extra_windows()
                return hwnd
        return None

    # 杀旧进程开新美图（避免两个窗口句柄混淆）
    import os as _os
    _os.system('taskkill /f /im XiuXiu.exe >nul 2>&1')
    time.sleep(0.5)
    subprocess.Popen([MEITU_EXE, torso_path])
    # 等新窗口出现，定位后返回
    for _ in range(30):
        time.sleep(0.2)
        new_hwnd = find_meitu()
        if new_hwnd:
            u.ShowWindow(new_hwnd, 9)
            time.sleep(0.3)
            u.SetWindowPos(new_hwnd, 0, 1280, 0, 1280, u.GetSystemMetrics(1), 0x0040)
            u.SetForegroundWindow(new_hwnd)
            time.sleep(0.5)  # 等窗口稳定
            return new_hwnd
    return None


def kill_extra_windows():
    """关闭非图片编辑的美图窗口（美图秀秀启动页、美图批处理等），只留图片编辑"""
    def cb(h, l):
        t = ctypes.create_unicode_buffer(256)
        u.GetWindowTextW(h, t, 256)
        pp = ctypes.c_uint32(0)
        u.GetWindowThreadProcessId(h, ctypes.byref(pp))
        tv = t.value
        # 包含圖片編輯/图片编辑 → 保留；其他美图窗口 → 关闭
        if tv and not ('圖片編輯' in tv or '图片编辑' in tv) and _has_title(t):
            if u.IsWindowVisible(h):
                u.PostMessageW(h, 0x0010, 0, 0)  # WM_CLOSE
        return True

    u.EnumWindows(
        ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)(cb), 0
    )


def enter_ai_sticker(hwnd):
    """进入AI贴图模式（AI面板未展开时才点）"""
    global _ai_panel_open
    if _ai_panel_open:
        return
    ff(hwnd)
    click(*BTN["AI_tools"], 1.0)
    click(*BTN["AI_sticker"], 1.0)
    _ai_panel_open = True


def reset_ai_panel():
    """标记AI面板已关闭（切胚衣后需要重新进入）"""
    global _ai_panel_open
    _ai_panel_open = False


def is_window_responding(hwnd):
    """检测窗口是否响应 — IsHungAppWindow（QT应用兼容）"""
    return ctypes.windll.user32.IsHungAppWindow(hwnd) == 0


def wait_sticker(before=None, center_x=0, center_y=0, timeout=0, hwnd=None):
    """贴图置入后等3D渲染完成 — 窗口移动检测

    每0.2s尝试移动美图窗口1px→移回原位。
    窗口能移动 = 已恢复响应 = 3D/渲染完成。
    最长等30s。
    """
    if not hwnd:
        time.sleep(0.5)
        return True

    org_x, org_y = 1280, 0
    for i in range(150):  # 最多等 30s
        # 右移1px
        u.SetWindowPos(hwnd, 0, org_x + 1, org_y, 0, 0, 0x0001)  # SWP_NOSIZE
        time.sleep(0.02)
        # 移回原位
        u.SetWindowPos(hwnd, 0, org_x, org_y, 0, 0, 0x0001)
        # 检查窗口是否真的在原始位置（没有卡死）
        rect = ctypes.wintypes.RECT()
        u.GetWindowRect(hwnd, ctypes.byref(rect))
        if rect.left == org_x:
            time.sleep(0.15)
            return True
        time.sleep(0.2)
    print("  [WARN] 窗口移动检测超时(30s)，强制继续")
    return True


def import_file(png_path):
    """打开文件对话框 → 粘贴路径 → 导入（兼容QT/标准对话框）"""
    dlg = None
    for _ in range(40):  # 最多等 4s
        def fh(h, l):
            nonlocal dlg
            cls = ctypes.create_unicode_buffer(64)
            u.GetClassNameW(h, cls, 64)
            if cls.value == "#32770" and u.IsWindowVisible(h):
                dlg = h
                return False
            # QT: 非主窗口的可见弹窗
            return True
        u.EnumWindows(
            ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)(fh), 0
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

    # 找到保存对话框（兼容QT和标准对话框）
    sv = None
    meitu_pid = ctypes.c_uint32(0)
    u.GetWindowThreadProcessId(hwnd, ctypes.byref(meitu_pid))

    def fsv(h, l):
        nonlocal sv
        cls = ctypes.create_unicode_buffer(64)
        u.GetClassNameW(h, cls, 64)
        title = ctypes.create_unicode_buffer(256)
        u.GetWindowTextW(h, title, 256)
        ppid = ctypes.c_uint32(0)
        u.GetWindowThreadProcessId(h, ctypes.byref(ppid))
        if u.IsWindowVisible(h):
            if ("ToolSa" in cls.value or "#32770" in cls.value or
                (ppid.value == meitu_pid.value and cls.value and title.value and
                 ("保存" in title.value or "Save" in title.value or "另存" in title.value))):
                sv = h
                return False
        return True

    for _ in range(15):
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

    import pyperclip as _pc
    output_name = os.path.basename(output_path)

    # 1) 填保存路径（文件夹路径）
    ff(sv)
    time.sleep(0.1)
    click(*BTN["save_path"], 0.15)
    time.sleep(0.05)
    key_comb(0x11, 0x41)  # Ctrl+A
    time.sleep(0.05)
    u.keybd_event(0x2E, 0, 0, 0)  # Del
    time.sleep(0.02)
    u.keybd_event(0x2E, 0, 2, 0)
    time.sleep(0.02)
    _pc.copy(folder_path)
    time.sleep(0.05)
    key_comb(0x11, 0x56)  # Ctrl+V
    time.sleep(0.15)

    # 2) 填文件名（去掉扩展名，对话框会自动加）
    output_name_noext = os.path.splitext(output_name)[0]
    ff(sv)
    time.sleep(0.1)
    click(*BTN["save_filename"], 0.2)
    time.sleep(0.05)
    key_comb(0x11, 0x41)
    time.sleep(0.05)
    _pc.copy(output_name_noext)
    time.sleep(0.05)
    key_comb(0x11, 0x56)
    time.sleep(0.15)

    # 3) 设置质量为100
    ff(sv)
    time.sleep(0.1)
    click(*BTN["save_qual"], 0.15)
    time.sleep(0.05)
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

    # 4) 点击保存
    ff(sv)
    click(*BTN["save_btn"], 0.2)

    # 等文件出现（最多15s）
    for _ in range(75):
        if os.path.exists(output_path) and os.path.getsize(output_path) > 50 * 1024:
            sz = os.path.getsize(output_path) // 1024
            print(f" [OK] {sz}KB", flush=True)
            return True
        time.sleep(0.2)

    print("  [WARN] save timeout, file not found")
    return False
