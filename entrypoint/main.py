"""入口点 — WB贴图 v3.0 (OS)

用法:
    python entrypoint/main.py                     ← 白T，自动扫描
    python entrypoint/main.py --black             ← 黑T，自动扫描
    python entrypoint/main.py DX0001              ← 指定文件夹（白T）
    python entrypoint/main.py --black DX0001      ← 指定文件夹（黑T）
"""

import sys, os

_project_root = os.path.dirname(os.path.dirname(__file__))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from workflow.pipeline import run_pipeline


def main():
    args = sys.argv[1:]
    is_black = "--black" in args
    args = [a for a in args if a != "--black"]
    single_folder = args[0] if args else None
    run_pipeline(is_black=is_black, single_folder=single_folder)


if __name__ == "__main__":
    main()
