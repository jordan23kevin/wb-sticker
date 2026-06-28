"""图像检测工具 — 深色检测(W3C相对亮度)、像素分析"""

import numpy as np
from PIL import Image

from config.settings import ALPHA_THRESHOLD, DARK_THRESHOLD


def _srgb_to_linear(c):
    """sRGB → 线性化（W3C标准）"""
    c = c / 255.0
    return np.where(c <= 0.03928, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def relative_luminance(rgb_pixels):
    """计算相对亮度（W3C标准）
       L = 0.2126*R + 0.7152*G + 0.0722*B
    """
    r, g, b = rgb_pixels[:, 0], rgb_pixels[:, 1], rgb_pixels[:, 2]
    r_l = _srgb_to_linear(r)
    g_l = _srgb_to_linear(g)
    b_l = _srgb_to_linear(b)
    return 0.2126 * r_l + 0.7152 * g_l + 0.0722 * b_l


def is_dark_image(png_path, threshold=None):
    """W3C相对亮度检测：L <= 0.5 → 深色背景"""
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
        L = relative_luminance(pixels).mean()
        return L <= threshold
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
