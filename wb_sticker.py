# -*- coding: utf-8 -*-
# 项目位置: E:\\Claude code\\WB 贴图\\
# 迁移自: E:\\wb-new-arrivals\\workspace\\WB-Material\\
# 版本: v2.6.0 | 更新日期: 2026-06-21
# 成功基线: DX0020-DX0035 全部白T+黑T 100%成功
"""
WB贴图 v2.6.0 — 主入口（支持白T/黑T）
爸爸说"WB贴图"就启动这个脚本。

命名规则：
  B → 背（白背2.jpg / 黑背2.jpg）
  W → 正（白正2.jpg / 黑正2.jpg）
  BW/WB → 先背再正

用法：
  python3 wb_sticker.py                     ← 白T，自动扫描
  python3 wb_sticker.py --black             ← 黑T，自动扫描
  python3 wb_sticker.py DX0001              ← 指定文件夹（白T）
  python3 wb_sticker.py --black DX0001      ← 指定文件夹（黑T）

项目位置：E:\\Claude code\\WB 贴图\\
依赖：pillow, numpy (uv run --with pillow --with numpy --with pyperclip python wb_sticker.py)
"""
import sys, os, io
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except:
    try: sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    except: pass
def get_type(filename):
    """根据文件名判断类型：B/b=背, W/w=正, BW/WB/bw/wb=先背后正
       不含B/W时按文件名最后一位数字: 1=背, 2=正"""
    stem = os.path.splitext(os.path.basename(filename))[0]
    s = stem.upper()
    if 'BW' in s or 'WB' in s:
        return 'both'
    elif 'B' in s:
        return 'back'
    elif 'W' in s:
        return 'front'
    # 无B/W，按数字尾数
    last = stem[-1]
    if last == '1': return 'back'
    if last == '2': return 'front'
    return None

def main():
    args = sys.argv[1:]
    is_black = '--black' in args
    args = [a for a in args if a != '--black']
    color_name = '黑T' if is_black else '白T'

    print("=" * 50)
    print(f"  WB贴图 v2.0 — {color_name}")
    print("=" * 50)
    print()

    from wb_sticker_tail2 import run_tail2, run_tail2_black
    from wb_sticker_tail1 import run_tail1, run_tail1_black
    run_tail2_fn = run_tail2_black if is_black else run_tail2
    run_tail1_fn = run_tail1_black if is_black else run_tail1

    if len(args) >= 1:
        folders = [args[0]]
        if len(args) >= 2:
            png = args[1]
            t = get_type(png)
            print(f"指定文件: {args[0]}/{png} → {t}")
            if t == 'front': run_tail2_fn(args[0], png)
            elif t == 'back': run_tail1_fn(args[0], png)
            elif t == 'both':
                run_tail1_fn(args[0], png)
                run_tail2_fn(args[0], png)
            else: print(f"⚠️ 无法判断类型: {png}")
            return
    else:
        base = 'D:\\Semems\\1AI'
        folders = sorted([d for d in os.listdir(base)
                         if os.path.isdir(os.path.join(base, d)) and d.startswith('DX')])

    print(f"待处理: {len(folders)} 个文件夹")
    for f in folders: print(f"  {f}")
    print()

    for dn in folders:
        dp = os.path.join('D:\\Semems\\1AI', dn)
        pngs = sorted([f for f in os.listdir(dp) if f.lower().endswith('.png')])
        for png in pngs:
            t = get_type(png)
            if t == 'front':
                print(f"\n{'='*40}\n  {dn}/{png} → 正")
                if not run_tail2_fn(dn, png):
                    print(f"  ❌ 正处理失败")
            elif t == 'back':
                print(f"\n{'='*40}\n  {dn}/{png} → 背")
                if not run_tail1_fn(dn, png):
                    print(f"  ❌ 背处理失败")
            elif t == 'both':
                print(f"\n{'='*40}\n  {dn}/{png} → 背(第一次)")
                ok = run_tail1_fn(dn, png)
                if ok:
                    print(f"\n{'='*40}\n  {dn}/{png} → 正(第二次)")
                    if not run_tail2_fn(dn, png):
                        print(f"  ❌ 正处理失败")
                else:
                    print(f"  ❌ 背处理失败，跳过正")
            else:
                print(f"\n⚠️ 跳过 {dn}/{png} — 文件名不含B/W")

if __name__ == "__main__":
    main()
