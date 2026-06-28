"""图像检测工具 — 深色检测、像素分析"""

import numpy as np
from PIL import Image

from config.settings import ALPHA_THRESHOLD, DARK_THRESHOLD


def is_dark_image(png_path, threshold=None):
    """检查图片是否过暗（非透明区域平均亮度 < threshold）"""
    if threshold is None:
        threshold = DARK_THRESHOLD
    try:
        img = Image.open(png_path).convert("RGBA")
        a = np.array(img)
        alpha = a[:, :, 3]
        mask = alpha >= ALPHA_THRESHOLD
        if not mask.any():
            return False
        pixels = a[:, :, :3][mask].astype(np.float64)
        avg_brightness = pixels.mean()
        return avg_brightness < threshold
    except Exception:
        return False


def calc_offset_back(png_path, target_x, target_y):
    """计算背图偏移量"""
    img = Image.open(png_path).convert("RGBA")
    a = np.array(img)
    h = a.shape[0]
    alpha = a[:, :, 3].astype(np.float64)
    mask = alpha >= ALPHA_THRESHOLD
    ys, xs = np.where(mask)
    weights = np.where(mask, alpha, 0.0)
    y_min = int(ys.min())
    for y in range(y_min, min(y_min + 200, h)):
        if (alpha[y] >= 20).sum() >= 50:
            y_min = y
            break
    cx = float((np.indices(alpha.shape)[1] * weights).sum() / weights.sum())
    scale = 360.0 / h
    dx = int(round(target_x - cx * scale - 1921))
    dy = int(round(target_y - y_min * scale - 590))
    return dx, dy
