"""文件名类型判断工具"""

import os


def get_type(filename: str) -> str | None:
    """判断贴图类型: back / front / both / None"""
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
    if last == '1':
        return 'back'
    if last == '2':
        return 'front'
    return None
