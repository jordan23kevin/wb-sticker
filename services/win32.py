"""Win32 API 服务层 — 窗口管理、鼠标键盘操作"""

import ctypes
import time
from ctypes import wintypes

u = ctypes.windll.user32
gdi = ctypes.windll.gdi32


def get_pixel(x, y):
    """获取屏幕 (x,y) 像素 RGB"""
    dc = u.GetDC(0)
    c = gdi.GetPixel(dc, x, y)
    u.ReleaseDC(0, dc)
    return c & 0xFF, (c >> 8) & 0xFF, (c >> 16) & 0xFF


def ff(hw):
    """Bring window to foreground"""
    tid = u.GetWindowThreadProcessId(hw, None)
    fg = u.GetForegroundWindow()
    ft = u.GetWindowThreadProcessId(fg, None)
    if ft != tid:
        u.AttachThreadInput(ft, tid, True)
    u.SetForegroundWindow(hw)
    time.sleep(0.02)
    try:
        ctypes.windll.user32.SwitchToThisWindow(hw, True)
    except Exception:
        pass
    time.sleep(0.03)
    if ft != tid:
        u.AttachThreadInput(ft, tid, False)


def click(x, y, d=0.03):
    """点击 (x,y)"""
    u.SetCursorPos(x, y)
    time.sleep(0.02)
    u.mouse_event(0x0002, 0, 0, 0, 0)  # down
    time.sleep(0.05)
    u.mouse_event(0x0004, 0, 0, 0, 0)  # up
    time.sleep(d)


def mdown(x, y):
    u.SetCursorPos(x, y)
    time.sleep(0.005)
    u.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.02)


def mmove(x, y):
    u.SetCursorPos(x, y)
    time.sleep(0.005)


def mup(d=0.1):
    u.mouse_event(0x0004, 0, 0, 0, 0)
    time.sleep(d)


def key_comb(c, vk):
    """组合键 Ctrl+Key"""
    u.keybd_event(c, 0, 0, 0)
    time.sleep(0.01)
    u.keybd_event(vk, 0, 0, 0)
    time.sleep(0.005)
    u.keybd_event(vk, 0, 2, 0)
    time.sleep(0.005)
    u.keybd_event(c, 0, 2, 0)
    time.sleep(0.01)


def drag(from_xy, to_xy, steps=8):
    """从 (fx,fy) 拖动到 (tx,ty)"""
    fx, fy = from_xy
    tx, ty = to_xy
    mdown(fx, fy)
    for i in range(steps):
        mmove(fx + int((tx - fx) * i / (steps - 1)),
              fy + int((ty - fy) * i / (steps - 1)))
        time.sleep(0.002)
    mup(0.08)
