"""
⚠️ 此文件已迁移到 OS 架构，请使用:
    python entrypoint/main.py [--black] [DX文件夹]

本文件作为向后兼容入口。
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from entrypoint.main import main
main()
