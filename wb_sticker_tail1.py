# -*- coding: utf-8 -*-
"""
WB贴图 v2.7.0 — 尾数1（背 = 白背2.jpg / 黑背2.jpg）
白T：旋转 + 内部拖动 + Alpha加权(TARGET_X=2115)
黑T：旋转 + 内部拖动 + Alpha加权(TARGET_X=2115) + 混合两步
成功基线: DX0020-DX0035 黑白全部 100% 零FAIL

用法：
  python3 wb_sticker_tail1.py DX0001              ← 白T
  python3 wb_sticker_tail1.py --black DX0001      ← 黑T
"""
import ctypes, time, subprocess, os, sys
from ctypes import wintypes
from PIL import Image
import numpy as np

MEITU_EXE = r"D:\Program Files\MeituApp\MeituApp\XiuXiu\XiuXiu.exe"
DEFAULT_LEFT = 1921; DEFAULT_TOP = 590; ALPHA_THRESHOLD = 20
DRAG_START = (2100, 720)

BTN = {
    "AI_tools":     (1320, 140),
    "AI_sticker":   (1460, 560),
    "add_image":    (1510, 678),
    "sel_sticker":  (2110, 800),
    "rotate_btn":   (2102, 993),
    "rotate_drop":  (2107, 993),
    "mix_norm":     (1566, 880),
    "mix_sel":      (1549, 931),
    "mix_cfm":      (1511, 940),
    "black_mix":    (1545, 878),
    "black_normal": (1545, 905),
    "save_path":    (2200, 555),
    "save_qual":    (2260, 758),
    "save_btn":     (2224, 985),
}

u = ctypes.windll.user32

def ff(hw):
    tid = u.GetWindowThreadProcessId(hw, None)
    fg = u.GetForegroundWindow()
    ft = u.GetWindowThreadProcessId(fg, None)
    if ft != tid: u.AttachThreadInput(ft, tid, True)
    u.SetForegroundWindow(hw); time.sleep(0.02)
    try: ctypes.windll.user32.SwitchToThisWindow(hw, True)
    except: pass
    time.sleep(0.03)
    if ft != tid: u.AttachThreadInput(ft, tid, False)

def click(x, y, d=0.03):
    u.SetCursorPos(x, y); time.sleep(0.02)
    u.mouse_event(0x0002, 0, 0, 0, 0); time.sleep(0.05)
    u.mouse_event(0x0004, 0, 0, 0, 0); time.sleep(d)

def mdown(x, y):
    u.SetCursorPos(x, y); time.sleep(0.005)
    u.mouse_event(0x0002, 0, 0, 0, 0); time.sleep(0.02)

def mmove(x, y):
    u.SetCursorPos(x, y); time.sleep(0.005)

def mup(d=0.1):
    u.mouse_event(0x0004, 0, 0, 0, 0); time.sleep(d)

def key_comb(c, vk):
    u.keybd_event(c, 0, 0, 0); time.sleep(0.01)
    u.keybd_event(vk, 0, 0, 0); time.sleep(0.005)
    u.keybd_event(vk, 0, 2, 0); time.sleep(0.005)
    u.keybd_event(c, 0, 2, 0); time.sleep(0.01)

def find_meitu():
    hwnd = u.FindWindowW(None, "美图秀秀-图片编辑")
    if hwnd: return hwnd
    def ecb(h, l):
        b = ctypes.create_unicode_buffer(256)
        u.GetWindowTextW(h, b, 256)
        if chr(32654) in b.value or chr(32645) in b.value:
            globals()['_hw'] = h; return False
        return True
    u.EnumWindows(ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)(ecb), 0)
    return globals().get('_hw')

def calc_offset(png_path, target_x, target_y):
    img = Image.open(png_path).convert("RGBA")
    a = np.array(img); h = a.shape[0]
    alpha = a[:,:,3].astype(np.float64)
    mask = alpha >= ALPHA_THRESHOLD
    ys, xs = np.where(mask)
    weights = np.where(mask, alpha, 0.0)
    y_min = int(ys.min())
    for y in range(y_min, min(y_min+200, h)):
        if (alpha[y] >= 20).sum() >= 50: y_min = y; break
    cx = float((np.indices(alpha.shape)[1] * weights).sum() / weights.sum())
    scale = 360.0 / h
    dx = int(round(target_x - cx * scale - DEFAULT_LEFT))
    dy = int(round(target_y - y_min * scale - DEFAULT_TOP))
    return dx, dy

def import_file(png_path):
    """Find file open dialog, paste path via pyperclip + Ctrl+V, press Enter"""
    dlg = None
    for _ in range(30):  # wait up to 3s for dialog
        def fh(h, l):
            nonlocal dlg
            cls = ctypes.create_unicode_buffer(64)
            u.GetClassNameW(h, cls, 64)
            if cls.value == '#32770' and u.IsWindowVisible(h):
                dlg = h; return False
            return True
        u.EnumWindows(ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)(fh), 0)
        if dlg: break
        time.sleep(0.1)
    if not dlg:
        print('  [FAIL] file dialog not found')
        return False
    ff(dlg)
    import pyperclip as _pc
    _pc.copy(png_path); time.sleep(0.05)
    key_comb(0x11, 0x41); time.sleep(0.05)
    u.keybd_event(0x2E, 0, 0, 0); time.sleep(0.02)
    u.keybd_event(0x2E, 0, 2, 0); time.sleep(0.05)
    key_comb(0x11, 0x56); time.sleep(0.1)
    u.keybd_event(0x0D, 0, 0, 0); time.sleep(0.02)
    u.keybd_event(0x0D, 0, 2, 0); time.sleep(0.1)
    return True
def do_mix(is_black):
    if is_black:
        click(*BTN["black_mix"], 0.3); time.sleep(0.3)
        click(*BTN["black_normal"], 0.15)
    else:
        click(*BTN["mix_norm"], 0.05)
        click(*BTN["mix_sel"], 0.05)
        click(*BTN["mix_cfm"], 0.05)

def _run(dx_folder, png_name, is_black):
    sep = chr(92)
    color_label = '\u9ed1T' if is_black else '\u767dT'
    target_x = 2115  # 黑白背统一
    target_y = 570
    torso_name = '\u9ed1\u80cc2.jpg' if is_black else '\u767d\u80cc2.jpg'
    torso = sep.join(['D:', 'Semems', '1\u80da\u8863', torso_name])
    
    folder_path = sep.join(['D:', 'Semems', '1AI', dx_folder])
    png_path = sep.join([folder_path, png_name])
    output_name = '\u9ed1\u80cc2_\u526f\u672c.jpg' if is_black else '\u767d\u80cc2_\u526f\u672c.jpg'
    output_path = sep.join([folder_path, output_name])
    
    dx, dy = calc_offset(png_path, target_x, target_y)
    print(f'{color_label} \u5c3e\u65701 — {dx_folder}/{png_name}')
    print(f'  TARGET_X={target_x}, dx={dx}, dy={dy}')
    print(f'  \u62d6\u52a8: ({DRAG_START[0]},{DRAG_START[1]}) -> ({DRAG_START[0]+dx},{DRAG_START[1]+dy})')
    # 检查是否已保存
    if os.path.exists(output_path) and os.path.getsize(output_path) > 50*1024:
        print(f'  \u2705 \u5df2\u5b58\u5728\uff0c\u8df3\u8fc7')
        return True
    
    hwnd = find_meitu()
    if not hwnd:
        # 首次启动：两次打开让图片大小正常
        subprocess.Popen([MEITU_EXE, torso]); time.sleep(1.5)
        hwnd = find_meitu()
        u.SetWindowPos(hwnd, 0, 1280, 0, 1280, u.GetSystemMetrics(1), 0x0040); time.sleep(0.3)
        ff(hwnd)
        key_comb(0x11, 0x57); time.sleep(0.1)
        u.keybd_event(0x0D, 0, 0, 0); time.sleep(0.02)
        u.keybd_event(0x0D, 0, 2, 0); time.sleep(0.1)
        subprocess.Popen([MEITU_EXE, torso]); time.sleep(1.5)
        hwnd = find_meitu()
        u.SetWindowPos(hwnd, 0, 1280, 0, 1280, u.GetSystemMetrics(1), 0x0040); time.sleep(0.3)
        ff(hwnd)
        click(*BTN["AI_tools"], 1.0)
        click(*BTN["AI_sticker"], 1.0)
    else:
        ff(hwnd)
        key_comb(0x11, 0x57); time.sleep(0.1)
        u.keybd_event(0x0D, 0, 0, 0); time.sleep(0.02)
        u.keybd_event(0x0D, 0, 2, 0); time.sleep(0.1)
        subprocess.Popen([MEITU_EXE, torso]); time.sleep(1.5)
        u.SetWindowPos(hwnd, 0, 1280, 0, 1280, u.GetSystemMetrics(1), 0x0040); time.sleep(0.3)
    
    ff(hwnd)
    click(*BTN["add_image"], 0.5)
    if not import_file(png_path):
        print('  [FAIL] import_file failed')
        return False
    
    ff(hwnd)
    click(*BTN["sel_sticker"], 0.08)
    
    # 旋转（黑白背统一）
    ff(hwnd); time.sleep(0.1)
    rx, ry = BTN["rotate_btn"]
    mdown(rx, ry)
    for s in range(2):
        mmove(rx + s + 1, ry); time.sleep(0.002)
    mup(0.08)
    time.sleep(0.1)
    click(*BTN["sel_sticker"], 0.08)

    # 从内部拖动
    ff(hwnd)
    sx, sy = DRAG_START
    mdown(sx, sy)
    for i in range(8):
        mmove(sx + int(dx * i / 7), sy + int(dy * i / 7)); time.sleep(0.002)
    mup(0.08)
    
    do_mix(is_black)
    
    # 保存前删目标文件（避免覆盖弹窗干扰路径设置）
    if os.path.exists(output_path):
        os.remove(output_path)
    
    ff(hwnd)
    key_comb(0x11, 0x53)
    sv = None
    def fsv(h, l):
        nonlocal sv
        cls = ctypes.create_unicode_buffer(64)
        u.GetClassNameW(h, cls, 64)
        if u.IsWindowVisible(h) and 'ToolSa' in cls.value:
            sv = h; return False
        return True
    for _ in range(5):  # 0.5s max
        u.EnumWindows(ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)(fsv), 0)
        if sv: break
        time.sleep(0.1)
    if not sv: return False
    
    ff(sv)
    import pyperclip as _pc
    # Click path field twice, verify focus via readback
    for _c in range(2):
        u.SetCursorPos(2200, 555); time.sleep(0.02)
        u.mouse_event(0x0002, 0, 0, 0, 0); time.sleep(0.05)
        u.mouse_event(0x0004, 0, 0, 0, 0); time.sleep(0.05)
    time.sleep(0.1)
    key_comb(0x11, 0x41); time.sleep(0.02)
    key_comb(0x11, 0x43); time.sleep(0.03)
    _focus = _pc.paste()
    if _focus and 'DX' in _focus:
        print(f'  [path] {_focus}')
    # Clear and paste new path
    u.keybd_event(0x2E, 0, 0, 0); time.sleep(0.02)
    u.keybd_event(0x2E, 0, 2, 0); time.sleep(0.02)
    _pc.copy(folder_path); time.sleep(0.05)
    u.keybd_event(0x11, 0, 0, 0); time.sleep(0.05)
    u.keybd_event(0x56, 0, 0, 0); time.sleep(0.03)
    u.keybd_event(0x56, 0, 2, 0); time.sleep(0.03)
    u.keybd_event(0x11, 0, 2, 0); time.sleep(0.1)
    ff(sv)
    click(*BTN["save_qual"], 0.1); time.sleep(0.1)
    u.keybd_event(0x11, 0, 0, 0); time.sleep(0.05)
    u.keybd_event(0x41, 0, 0, 0); time.sleep(0.03)
    u.keybd_event(0x41, 0, 2, 0); time.sleep(0.03)
    u.keybd_event(0x11, 0, 2, 0); time.sleep(0.05)
    u.keybd_event(0x2E, 0, 0, 0); time.sleep(0.02)
    u.keybd_event(0x2E, 0, 2, 0); time.sleep(0.02)
    import pyperclip as _pc; _pc.copy('100'); time.sleep(0.05)
    u.keybd_event(0x11, 0, 0, 0); time.sleep(0.05)
    u.keybd_event(0x56, 0, 0, 0); time.sleep(0.03)
    u.keybd_event(0x56, 0, 2, 0); time.sleep(0.03)
    u.keybd_event(0x11, 0, 2, 0); time.sleep(0.1)
    ff(sv)
    click(*BTN["save_btn"], 0.1)
    
    _before = set(os.listdir(folder_path)) if os.path.isdir(folder_path) else set()
    for _ in range(15):  # 3s max wait for file
        if os.path.exists(output_path) and os.path.getsize(output_path) > 50*1024:
            sz = os.path.getsize(output_path) // 1024
            u.keybd_event(0x1B, 0, 2, 0); time.sleep(0.1)
            u.keybd_event(0x1B, 0, 0, 0); time.sleep(0.05)
            print(f'  ✅ {{sz}}KB'); return True
        for _alt in os.listdir(folder_path) if os.path.isdir(folder_path) else []:
            if _alt.endswith('.jpg') and _alt not in _before:
                _ap = os.path.join(folder_path, _alt)
                if os.path.getsize(_ap) > 50*1024:
                    if os.path.exists(output_path): os.remove(output_path)
                    os.rename(_ap, output_path)
                    sz = os.path.getsize(output_path) // 1024
                    print(f'  ✅ {{sz}}KB'); return True
        time.sleep(0.2)
    return False

def run_tail1(dx_folder, png_name=None):
    sep = chr(92)
    fp = sep.join(['D:', 'Semems', '1AI', dx_folder])
    if not png_name:
        ps = [f for f in os.listdir(fp) if f.lower().endswith('.png')]
        if not ps: return False
        png_name = ps[0]
    return _run(dx_folder, png_name, is_black=False)

def run_tail1_black(dx_folder, png_name=None):
    sep = chr(92)
    fp = sep.join(['D:', 'Semems', '1AI', dx_folder])
    if not png_name:
        ps = [f for f in os.listdir(fp) if f.lower().endswith('.png')]
        if not ps: return False
        png_name = ps[0]
    return _run(dx_folder, png_name, is_black=True)

if __name__ == "__main__":
    args = sys.argv[1:]
    is_black = '--black' in args
    args = [a for a in args if a != '--black']
    if len(args) < 1:
        print("用法: python3 wb_sticker_tail1.py [--black] <DX文件夹> [文件名]"); sys.exit(1)
    if is_black:
        run_tail1_black(args[0], args[1] if len(args) >= 2 else None)
    else:
        run_tail1(args[0], args[1] if len(args) >= 2 else None)
