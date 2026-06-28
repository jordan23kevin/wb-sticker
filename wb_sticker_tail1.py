"""
⚠️ 此文件已迁移到 OS 架构:
    core/back.py  → process_back()

本文件作为向后兼容入口。
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from core.back import process_back
from config.settings import SOURCE_BASE
import os as _os

def run_tail1(dx_folder, png_name=None):
    return process_back(dx_folder, png_name, is_black=False)

def run_tail1_black(dx_folder, png_name=None):
    return process_back(dx_folder, png_name, is_black=True)

def is_dark_image(png_path, threshold=80):
    from utils.detector import is_dark_image as _d
    return _d(png_path, threshold)

if __name__ == "__main__":
    args = sys.argv[1:]
    is_black = "--black" in args
    args = [a for a in args if a != "--black"]
    fn = run_tail1_black if is_black else run_tail1
    fn(args[0], args[1] if len(args) >= 2 else None)
