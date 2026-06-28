"""
⚠️ 此文件已迁移到 OS 架构:
    core/front.py  → process_front()

本文件作为向后兼容入口。
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from core.front import process_front

def run_tail2(dx_folder, png_name=None):
    return process_front(dx_folder, png_name, is_black=False)

def run_tail2_black(dx_folder, png_name=None):
    return process_front(dx_folder, png_name, is_black=True)

if __name__ == "__main__":
    args = sys.argv[1:]
    is_black = "--black" in args
    args = [a for a in args if a != "--black"]
    fn = run_tail2_black if is_black else run_tail2
    fn(args[0], args[1] if len(args) >= 2 else None)
