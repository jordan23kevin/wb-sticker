# -*- coding: utf-8 -*-
"""
WB贴图 — 尾数2（正 = 白正2.jpg / 黑正2.jpg）
白T：从右下角(1906,973)→(2166,705)，混合三步
黑T：从右下角(1906,973)→(2166,705)，混合两步(1545,878→1545,905)

用法：
  python3 wb_sticker_tail2.py DX0001              ← 白T
  python3 wb_sticker_tail2.py --black DX0001      ← 黑T
"""
import ctypes, time, subprocess, os, sys
from ctypes import wintypes

MEITU_EXE = r"D:\Program Files\MeituApp\MeituApp\XiuXiu\XiuXiu.exe"

BTN = {
    "AI_tools":     (1340, 120),
    "AI_sticker":   (1460, 560),
    "add_image":    (1510, 678),
    "sel_sticker":  (2110, 800),
    "rotate_btn":   (2102, 993),
    "rotate_drop":  (2107, 993),
    "drag_from":    (1906, 973),
    "drag_to":      (2166, 705),
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
    u.SetForegroundWindow(hw); time.sleep(0.03)
    try: ctypes.windll.user32.SwitchToThisWindow(hw, True)
    except: pass
    time.sleep(0.03)
    if ft != tid: u.AttachThreadInput(ft, tid, False)

def click(x, y, d=0.05):
    u.SetCursorPos(x, y); time.sleep(0.02)
    u.mouse_event(0x0002, 0, 0, 0, 0); time.sleep(0.05)
    u.mouse_event(0x0004, 0, 0, 0, 0); time.sleep(d)

def mdown(x, y):
    u.SetCursorPos(x, y); time.sleep(0.01)
    u.mouse_event(0x0002, 0, 0, 0, 0); time.sleep(0.02)

def mmove(x, y):
    u.SetCursorPos(x, y); time.sleep(0.01)

def mup(d=0.1):
    u.mouse_event(0x0004, 0, 0, 0, 0); time.sleep(d)

def key_comb(c, vk):
    u.keybd_event(c, 0, 0, 0); time.sleep(0.02)
    u.keybd_event(vk, 0, 0, 0); time.sleep(0.01)
    u.keybd_event(vk, 0, 2, 0); time.sleep(0.01)
    u.keybd_event(c, 0, 2, 0); time.sleep(0.03)

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

def import_file(png_path):
    dlg = None
    def fh(h, l):
        nonlocal dlg
        cls = ctypes.create_unicode_buffer(64)
        u.GetClassNameW(h, cls, 64)
        if cls.value == '#32770' and u.IsWindowVisible(h):
            dlg = h; return False
        return True
    u.EnumWindows(ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)(fh), 0)
    if not dlg: return False
    ff(dlg)
    edit = None
    def fe(h, l):
        nonlocal edit
        cls = ctypes.create_unicode_buffer(64)
        u.GetClassNameW(h, cls, 64)
        if cls.value == 'Edit' and u.IsWindowVisible(h):
            edit = h; return False
        return True
    u.EnumChildWindows(dlg, ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)(fe), 0)
    if edit:
        u.SetFocus(edit); time.sleep(0.02)
        key_comb(0x11, 0x41); time.sleep(0.03)
        u.keybd_event(0x2E, 0, 0, 0); time.sleep(0.02)
        u.keybd_event(0x2E, 0, 2, 0); time.sleep(0.05)
        ctypes.windll.user32.SendMessageW(edit, 0x000C, 0, png_path)
        time.sleep(0.2)
    ob = None
    def fob(h, l):
        nonlocal ob
        cls = ctypes.create_unicode_buffer(64)
        ttl = ctypes.create_unicode_buffer(256)
        u.GetClassNameW(h, cls, 64)
        u.GetWindowTextW(h, ttl, 256)
        if cls.value == 'Button' and u.IsWindowVisible(h) and '\u6253\u5f00' in ttl.value:
            ob = h
        return True
    u.EnumChildWindows(dlg, ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)(fob), 0)
    if ob: ctypes.windll.user32.SendMessageW(ob, 0x00F5, 0, 0)
    else: u.SendMessageW(dlg, 0x0100, 0x0D, 0)
    time.sleep(1)
    return True

def do_mix(is_black):
    """混合模式：白T三步，黑T两步"""
    if is_black:
        click(*BTN["black_mix"], 0.3)
        time.sleep(0.3)
        click(*BTN["black_normal"], 0.3)
    else:
        click(*BTN["mix_norm"], 0.05)
        click(*BTN["mix_sel"], 0.05)
        click(*BTN["mix_cfm"], 0.1)

def _run(dx_folder, png_name, is_black):
    sep = chr(92)
    torso = sep.join(['D:', 'Semems', '1胚衣', '黑正2.jpg' if is_black else '白正2.jpg'])
    folder_path = sep.join(['D:', 'Semems', '1AI', dx_folder])
    png_path = sep.join([folder_path, png_name])
    output_name = '黑正2_副本.jpg' if is_black else '白正2_副本.jpg'
    output_path = sep.join([folder_path, output_name])
    
    color = '黑T' if is_black else '白T'
    print(f'{color} \u5c3e\u65702 — {dx_folder}/{png_name}', flush=True)
    
    # 检查是否已保存
    if os.path.exists(output_path) and os.path.getsize(output_path) > 50*1024:
        print(f'  \u2705 \u5df2\u5b58\u5728\uff0c\u8df3\u8fc7')
        return True
    
    # 启动/切换胚衣
    hwnd = find_meitu()
    if not hwnd:
        # 首次启动：两次打开让图片大小正常
        subprocess.Popen([MEITU_EXE, torso]); time.sleep(4)
        hwnd = find_meitu()
        u.SetWindowPos(hwnd, 0, 1280, 0, 1280, u.GetSystemMetrics(1), 0x0040); time.sleep(0.3)
        ff(hwnd)
        key_comb(0x11, 0x57); time.sleep(0.5)
        u.keybd_event(0x0D, 0, 0, 0); time.sleep(0.02)
        u.keybd_event(0x0D, 0, 2, 0); time.sleep(0.5)
        subprocess.Popen([MEITU_EXE, torso]); time.sleep(4)
        hwnd = find_meitu()
        u.SetWindowPos(hwnd, 0, 1280, 0, 1280, u.GetSystemMetrics(1), 0x0040); time.sleep(0.3)
        ff(hwnd)
        click(*BTN["AI_tools"], 1.0)
        click(*BTN["AI_sticker"], 1.0)
    else:
        ff(hwnd)
        key_comb(0x11, 0x57); time.sleep(0.5)
        u.keybd_event(0x0D, 0, 0, 0); time.sleep(0.02)
        u.keybd_event(0x0D, 0, 2, 0); time.sleep(0.3)
        subprocess.Popen([MEITU_EXE, torso]); time.sleep(3)
        u.SetWindowPos(hwnd, 0, 1280, 0, 1280, u.GetSystemMetrics(1), 0x0040); time.sleep(0.3)
    
    ff(hwnd)
    click(*BTN["add_image"], 1.0)
    if not import_file(png_path): return False
    
    ff(hwnd)
    click(*BTN["sel_sticker"], 0.3)
    ff(hwnd); time.sleep(0.2)
    rx, ry = BTN["rotate_btn"]
    mdown(rx, ry)
    for s in range(6):
        mmove(rx + s + 1, ry); time.sleep(0.01)
    mup(0.3)
    time.sleep(0.2)
    click(*BTN["sel_sticker"], 0.3)
    
    ff(hwnd)
    fx, fy = BTN["drag_from"]
    tx, ty = BTN["drag_to"]
    mdown(fx, fy)
    for i in range(26):
        mmove(fx + int((tx-fx)*i/25), fy + int((ty-fy)*i/25)); time.sleep(0.008)
    mup(0.3)
    
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
    for _ in range(50):
        u.EnumWindows(ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)(fsv), 0)
        if sv: break
        time.sleep(0.1)
    if not sv: return False
    
    import pyperclip as _pc
    ff(sv)
    # 点击路径框→Ctrl+A→Delete→pyperclip→Ctrl+V
    u.SetCursorPos(2200, 555); time.sleep(0.03)
    u.mouse_event(0x0002, 0, 0, 0, 0); time.sleep(0.08)
    u.mouse_event(0x0004, 0, 0, 0, 0); time.sleep(0.2)
    u.keybd_event(0x11, 0, 0, 0); time.sleep(0.05)
    u.keybd_event(0x41, 0, 0, 0); time.sleep(0.03)
    u.keybd_event(0x41, 0, 2, 0); time.sleep(0.03)
    u.keybd_event(0x11, 0, 2, 0); time.sleep(0.05)
    u.keybd_event(0x2E, 0, 0, 0); time.sleep(0.02)
    u.keybd_event(0x2E, 0, 2, 0); time.sleep(0.02)
    _pc.copy(folder_path); time.sleep(0.05)
    u.keybd_event(0x11, 0, 0, 0); time.sleep(0.05)
    u.keybd_event(0x56, 0, 0, 0); time.sleep(0.03)
    u.keybd_event(0x56, 0, 2, 0); time.sleep(0.03)
    u.keybd_event(0x11, 0, 2, 0); time.sleep(0.1)
    ff(sv)
    # 质量100
    click(*BTN["save_qual"], 0.1); time.sleep(0.1)
    u.keybd_event(0x11, 0, 0, 0); time.sleep(0.05)
    u.keybd_event(0x41, 0, 0, 0); time.sleep(0.03)
    u.keybd_event(0x41, 0, 2, 0); time.sleep(0.03)
    u.keybd_event(0x11, 0, 2, 0); time.sleep(0.05)
    u.keybd_event(0x2E, 0, 0, 0); time.sleep(0.02)
    u.keybd_event(0x2E, 0, 2, 0); time.sleep(0.02)
    _pc.copy('100'); time.sleep(0.05)
    u.keybd_event(0x11, 0, 0, 0); time.sleep(0.05)
    u.keybd_event(0x56, 0, 0, 0); time.sleep(0.03)
    u.keybd_event(0x56, 0, 2, 0); time.sleep(0.03)
    u.keybd_event(0x11, 0, 2, 0); time.sleep(0.1)
    ff(sv)
    click(*BTN["save_btn"], 0.5)
    
    _before = set(os.listdir(folder_path)) if os.path.isdir(folder_path) else set()
    _defdir = sep.join(['D:', 'Semems', '1AI', 'DX0012'])
    for i in range(60):
        # 检查目标文件夹
        if os.path.exists(output_path) and os.path.getsize(output_path) > 50*1024:
            sz = os.path.getsize(output_path) // 1024
            print(f'  \u2705 {sz}KB'); return True
        # 检查美图自动命名的备选文件名
        for _alt in os.listdir(folder_path) if os.path.isdir(folder_path) else []:
            if _alt.endswith('.jpg') and _alt not in _before:
                _ap = os.path.join(folder_path, _alt)
                if os.path.getsize(_ap) > 50*1024:
                    if os.path.exists(output_path): os.remove(output_path)
                    os.rename(_ap, output_path)
                    sz = os.path.getsize(output_path) // 1024
                    print(f'  \u2705 {sz}KB (\u81ea\u52a8\u547d\u540d)'); return True
        # 检查DX0012
        for _alt2 in os.listdir(_defdir) if os.path.isdir(_defdir) else []:
            if _alt2.endswith('.jpg'):
                _ap2 = os.path.join(_defdir, _alt2)
                if os.path.getsize(_ap2) > 50*1024:
                    if os.path.exists(output_path): os.remove(output_path)
                    os.rename(_ap2, output_path)
                    sz = os.path.getsize(output_path) // 1024
                    print(f'  \u2705 {sz}KB (\u4eceDX0012)'); return True
        if i > 0 and i % 20 == 0: print(f'  {i*0.5:.0f}s')
        time.sleep(0.5)
    return False

def run_tail2(dx_folder, png_name=None):
    sep = chr(92)
    folder_path = sep.join(['D:', 'Semems', '1AI', dx_folder])
    if not png_name:
        pngs = [f for f in os.listdir(folder_path) if f.lower().endswith('.png')]
        if not pngs: return False
        png_name = pngs[0]
    return _run(dx_folder, png_name, is_black=False)

def run_tail2_black(dx_folder, png_name=None):
    sep = chr(92)
    folder_path = sep.join(['D:', 'Semems', '1AI', dx_folder])
    if not png_name:
        pngs = [f for f in os.listdir(folder_path) if f.lower().endswith('.png')]
        if not pngs: return False
        png_name = pngs[0]
    return _run(dx_folder, png_name, is_black=True)

if __name__ == "__main__":
    args = sys.argv[1:]
    is_black = '--black' in args
    args = [a for a in args if a != '--black']
    if len(args) < 1:
        print("用法: python3 wb_sticker_tail2.py [--black] <DX文件夹> [文件名]"); sys.exit(1)
    if is_black:
        run_tail2_black(args[0], args[1] if len(args) >= 2 else None)
    else:
        run_tail2(args[0], args[1] if len(args) >= 2 else None)
