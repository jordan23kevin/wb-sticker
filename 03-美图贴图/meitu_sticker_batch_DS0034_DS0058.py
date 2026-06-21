# -*- coding: utf-8 -*-
# Meitu Sticker v3.1
TARGET_X=2105;TARGET_Y=620
import ctypes,time,subprocess,os,sys,re,json
from ctypes import wintypes
u=ctypes.windll.user32
TORSO_PATH=r"D:\Semems\1胚衣\白正2.jpg"
MEITU_EXE=r"D:\Program Files\MeituApp\MeituApp\XiuXiu\XiuXiu.exe"
STICKER_BASE=r"D:\Semems\0AI"
TRACK_FILE=r"D:\Semems\0AI\.processed.json"
COORDS_FILE=r"E:\Hermes\项目\美图贴图\coords.json"
DS=0.02;DL=0.05;DM=0.15

# 加载坐标配置
with open(COORDS_FILE,"r",encoding="utf-8") as f:COORDS_CFG=json.load(f)
REF=COORDS_CFG["ref_window"]
BTN=COORDS_CFG["buttons"]

# 获取窗口rect
def get_rect(hwnd):
    r=wintypes.RECT();u.GetWindowRect(hwnd,ctypes.byref(r));return r

# 根据当前窗口计算绝对坐标
def calc(btn_name):
    r_cur=get_rect(current_hwnd)
    rel=BTN[btn_name]
    # 缩放比例
    sx=(r_cur.right-r_cur.left)/REF["width"]
    sy=(r_cur.bottom-r_cur.top)/REF["height"]
    return int(r_cur.left+rel[0]*sx),int(r_cur.top+rel[1]*sy)

current_hwnd=None

def fm():
    f=[None]
    def ep(h,l):
        b=ctypes.create_unicode_buffer(256);u.GetWindowTextW(h,b,256);t=b.value
        if t and ("\u7f8e\u5716" in t or "\u7f8e\u56fe" in t):f[0]=h;return False
        return True
    u.EnumWindows(ctypes.WINFUNCTYPE(wintypes.BOOL,wintypes.HWND,wintypes.LPARAM)(ep),0);return f[0]

def find_dlg():
    f=[None]
    def ep(h,l):
        cls=ctypes.create_unicode_buffer(64);u.GetClassNameW(h,cls,64)
        if cls.value=="#32770" and u.IsWindowVisible(h):f[0]=h;return False
        return True
    u.EnumWindows(ctypes.WINFUNCTYPE(wintypes.BOOL,wintypes.HWND,wintypes.LPARAM)(ep),0);return f[0]

def find_savedlg():
    f=[None]
    def ep(h,l):
        cls=ctypes.create_unicode_buffer(64);u.GetClassNameW(h,cls,64);ttl=ctypes.create_unicode_buffer(256);u.GetWindowTextW(h,ttl,256)
        if u.IsWindowVisible(h) and "ToolSa" in cls.value:f[0]=h;return False
        return True
    u.EnumWindows(ctypes.WINFUNCTYPE(wintypes.BOOL,wintypes.HWND,wintypes.LPARAM)(ep),0);return f[0]

def ff(h):
    global current_hwnd;current_hwnd=h
    tid=u.GetWindowThreadProcessId(h,None);fg=u.GetForegroundWindow();ft=u.GetWindowThreadProcessId(fg,None)
    if ft!=tid:u.AttachThreadInput(ft,tid,True)
    u.ShowWindow(h,9);time.sleep(0.05)
    u.SetWindowPos(h,-1,0,0,0,0,0x0001|0x0002|0x0040);time.sleep(0.03)
    u.SetForegroundWindow(h);time.sleep(0.05);u.BringWindowToTop(h);time.sleep(0.03)
    try:ctypes.windll.user32.SwitchToThisWindow(h,True)
    except:pass
    time.sleep(0.05)
    if ft!=tid:u.AttachThreadInput(ft,tid,False)
    u.SetWindowPos(h,-2,0,0,0,0,0x0001|0x0002|0x0040);time.sleep(0.03)

def ck(name,**kw):
    x,y=calc(name);click(x,y,**kw)

def click(x,y,d=DS):
    u.SetCursorPos(x,y);time.sleep(0.01)
    u.mouse_event(0x0002,0,0,0,0);time.sleep(DS)
    u.mouse_event(0x0004,0,0,0,0);time.sleep(d)

def mdown(x,y):u.SetCursorPos(x,y);time.sleep(0.01);u.mouse_event(0x0002,0,0,0,0);time.sleep(DS)
def mmove(x,y):u.SetCursorPos(x,y);time.sleep(0.01)
def mup():u.mouse_event(0x0004,0,0,0,0);time.sleep(DS)
def kd(k):u.keybd_event(k,0,0,0)
def ku(k):u.keybd_event(k,0,2,0)
def key(c,vk):kd(c);time.sleep(0.02);kd(vk);time.sleep(0.01);ku(vk);time.sleep(0.01);ku(c);time.sleep(DS)
def cs():key(0x11,0x53)
def ca():key(0x11,0x41)
def paste(t):
    subprocess.run(["powershell","-Command","Set-Clipboard -Value '"+t+"'"],capture_output=True,timeout=5)
    time.sleep(0.05);kd(0x11);time.sleep(0.05);kd(0x56);time.sleep(0.03);ku(0x56);time.sleep(0.03);ku(0x11);time.sleep(DL)

def delsel():
    subprocess.run(['powershell','-ExecutionPolicy','Bypass','-Command','Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait("{DELETE}")'],capture_output=True,timeout=10)
    time.sleep(DL)

from PIL import Image as _I
import numpy as _N
ALPHA_THRESHOLD=20

def get_off(p):
    try:
        img=_I.open(p).convert("RGBA");a=_N.array(img);h=a.shape[0]
        alpha=a[:,:,3].astype(_N.float64)
        mask=alpha>=ALPHA_THRESHOLD
        if not mask.any():return 0,0
        ys,xs=_N.where(mask)
        weights=_N.where(mask,alpha,0.0)
        y_min=int(ys.min())
        # 工业版透明图中轴线：Alpha>=20 的透明度加权重心，避免不规则透明图被左右边界拉偏
        cx=float((_N.indices(alpha.shape)[1]*weights).sum()/weights.sum())
        s=360.0/h;dy=int(round(TARGET_Y-y_min*s-590));dx=int(round(TARGET_X-cx*s-1921))
        return dx,dy
    except:return 0,0

def api_open(fp):
    dlg=find_dlg()
    if not dlg:return False
    ff(dlg)
    ed=[None]
    def ep(h,l):
        cls=ctypes.create_unicode_buffer(64);u.GetClassNameW(h,cls,64)
        if cls.value=="Edit":ed[0]=h;return False
        return True
    u.EnumChildWindows(dlg,ctypes.WINFUNCTYPE(wintypes.BOOL,wintypes.HWND,wintypes.LPARAM)(ep),0)
    bn=[None]
    def ep2(h,l):
        cls=ctypes.create_unicode_buffer(64);u.GetClassNameW(h,cls,64);ttl=ctypes.create_unicode_buffer(256);u.GetWindowTextW(h,ttl,256)
        if cls.value=="Button" and "\u6253\u5f00" in ttl.value:bn[0]=h;return False
        return True
    u.EnumChildWindows(dlg,ctypes.WINFUNCTYPE(wintypes.BOOL,wintypes.HWND,wintypes.LPARAM)(ep2),0)
    if ed[0]:u.SetFocus(ed[0]);time.sleep(0.02);ctypes.windll.user32.SendMessageW(ed[0],0x000C,0,fp)
    if bn[0]:ctypes.windll.user32.SendMessageW(bn[0],0x00F5,0,0)
    else:ctypes.windll.user32.SendMessageW(dlg,0x0100,0x0D,0)
    return True

def save_to(df):
    of=os.path.join(df,"\u767d\u6b632_\u526f\u672c.jpg")
    if os.path.exists(of):os.remove(of)
    cs()
    for _ in range(20):
        sv=find_savedlg()
        if sv:break
        time.sleep(0.1)
    if not sv:return False
    ff(sv)
    ck("save_path",d=DL);ca();kd(0x2E);time.sleep(DS);ku(0x2E);time.sleep(DS)
    paste(df);time.sleep(DL)
    ck("save_qual",d=DL);ca();kd(0x2E);time.sleep(DS);ku(0x2E);time.sleep(DS)
    paste("100");time.sleep(DL)
    ck("save_btn",d=DM)
    for i in range(20):
        if os.path.exists(of) and os.path.getsize(of)>50*1024:
            print("  [OK] %dKB"%(os.path.getsize(of)//1024));return True
        time.sleep(0.25)
    return False

def load_t():
    try:
        with open(TRACK_FILE,"r",encoding="utf-8-sig") as f:return json.load(f)
    except:return {"version":"2.2","processed":[],"last_pos":None}

def save_t(t):
    with open(TRACK_FILE,"w",encoding="utf-8") as f:json.dump(t,f,indent=2,ensure_ascii=False)

def mark(dn,lp=None):
    t=load_t()
    if dn not in t["processed"]:t["processed"].append(dn)
    if lp:t["last_pos"]=list(lp)
    save_t(t);print("  [TRACK] %s"%dn)

def get_unpro():
    # 按用户要求强制处理 DS0034-DS0058，不受 .processed.json 限制
    ds=[]
    for n in range(34,59):
        d=f"DS{n:04d}"
        if os.path.isdir(os.path.join(STICKER_BASE,d)):
            ds.append(d)
        else:
            print(f"  [MISS] {d}")
    return ds

def main():
    global current_hwnd
    print("="*50);print("Meitu Sticker v3.1 RANGE DS0034-DS0058");print("Target X=%d Y=%d"%(TARGET_X,TARGET_Y));print("="*50)
    up=get_unpro()
    print("Unprocessed: %d"%len(up))
    for d in up:print("  %s"%d)
    if not up:print("All done!");return
    print("Start 3s...");time.sleep(3)
    hwnd=None;lp=None;ok=0
    for i,dn in enumerate(up):
        dp=os.path.join(STICKER_BASE,dn)
        pngs=[f for f in os.listdir(dp) if f.lower().endswith(".png") and f!="\u767d\u6b632_\u526f\u672c.jpg"]
        if not pngs:print("\n[SKIP] %s"%dn);continue
        sp=os.path.join(dp,pngs[0])
        print("\n--- %s (%d/%d) ---"%(dn,i+1,len(up)))
        dx,dy=get_off(sp);print("  Offset: move(%+d,%+d)"%(dx,dy))
        if hwnd is None:
            subprocess.run(["taskkill","/F","/IM","XiuXiu.exe"],capture_output=True,timeout=5);time.sleep(0.5)
            subprocess.Popen([MEITU_EXE,TORSO_PATH]);time.sleep(4)
            hwnd=fm()
            if not hwnd:print("[FAIL] No meitu");continue
            u.SetWindowPos(hwnd,0,1280,0,1280,u.GetSystemMetrics(1),0x0040);time.sleep(0.3)
            ff(hwnd)
            ck("AI_tools",d=DM);time.sleep(1.0);ck("AI_sticker",d=DM);time.sleep(1.0);ck("add_image",d=DM)
            for _ in range(30):
                dlg=find_dlg()
                if dlg:break
                time.sleep(0.05)
            if not api_open(sp):print("[FAIL] File dialog");continue
            for _ in range(30):
                dlg=find_dlg()
                if not dlg:break
                time.sleep(0.05)
            print("  [OK] Loaded")
            ff(hwnd);ck("sel_sticker",d=DM)
            r_btn=calc("rotate_btn");r_drop=calc("rotate_drop")
            mdown(r_btn[0],r_btn[1]);mmove(r_drop[0],r_drop[1]);mup()
            sx,sy=calc("sel_sticker");ck("sel_sticker",d=DM);tx,ty=sx+dx,sy+dy
            mdown(sx,sy);mmove(tx,ty);mup();time.sleep(0.2);click(tx,ty,DM)
            print("  [OK] ("+str(tx)+","+str(ty)+")")
            ck("mix_norm",d=DS);ck("mix_sel",d=DS);ck("mix_cfm",d=DS)
            if save_to(dp):ok+=1;lp=(tx,ty);mark(dn,lp)
        else:
            if hwnd and lp:
                ff(hwnd)
                # 删除旧贴图
                lp_btn=calc("sel_sticker");click(lp_btn[0],lp_btn[1],DM);delsel()
                ck("add_image",d=DM)
                for _ in range(30):
                    dlg=find_dlg()
                    if dlg:break
                    time.sleep(0.05)
                if not api_open(sp):print("[FAIL] File dialog");continue
                for _ in range(30):
                    dlg=find_dlg()
                    if not dlg:break
                    time.sleep(0.05)
                print("  [OK] Loaded")
                ff(hwnd)
                # 选中新贴图+旋转
                ck("sel_sticker",d=DM)
                rb=calc("rotate_btn");rd=calc("rotate_drop")
                mdown(rb[0],rb[1]);mmove(rd[0],rd[1]);mup()
                sx,sy=calc("sel_sticker");ck("sel_sticker",d=DM);tx,ty=sx+dx,sy+dy;mdown(sx,sy);mmove(tx,ty);mup();time.sleep(0.2);click(tx,ty,DM)
                print("  [OK] ("+str(tx)+","+str(ty)+")")
                ck("mix_norm",d=DS);ck("mix_sel",d=DS);ck("mix_cfm",d=DS)
                if save_to(dp):ok+=1;lp=(tx,ty);mark(dn,lp)
        time.sleep(1)
    print("\n=== Done: %d/%d ==="%(ok,len(up)))
    print("完成！美图已保留查看")

if __name__=="__main__":main()
