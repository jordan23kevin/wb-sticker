"""WB贴图配置 — 路径、坐标、阈值"""

# 美图秀秀
MEITU_EXE = r"D:\Program Files\MeituApp\MeituApp\XiuXiu\XiuXiu.exe"

# 胚衣路径
BASE_TORSO = r"D:\Semems\1胚衣"
SOURCE_BASE = r"D:\Semems WB\02_PROJECTS"

# 贴图坐标（美图窗口 1280x 位置）
BTN = {
    "AI_tools":     (1320, 140),
    "AI_sticker":   (1460, 560),
    "add_image":    (1510, 678),
    "sel_sticker":  (2110, 800),
    "rotate_btn":   (2102, 993),
    "rotate_drop":  (2107, 993),
    "mix_norm":     (1566, 880),
    "mix_sel":      (1549, 931),
    "mix_cfm":      (1511, 940),
    "black_mix":    (1545, 878),
    "black_normal": (1545, 905),
    "save_path":    (2200, 555),
    "save_filename": (2180, 628),
    "save_qual":    (2260, 758),
    "save_btn":     (2224, 985),
}

# 尾数1（背）专用
TAIL1 = {
    "DEFAULT_LEFT": 1921,
    "DEFAULT_TOP": 590,
    "ALPHA_THRESHOLD": 20,
    "DRAG_START": (2100, 720),
    "TARGET_X": 2115,
    "TARGET_Y": 570,
}

# 尾数2（正）专用
TAIL2 = {
    "drag_from": (1906, 973),
    "drag_to":   (2166, 705),
}

# 图像参数
ALPHA_THRESHOLD = 20
DARK_THRESHOLD = 80
MIN_FILE_SIZE = 50 * 1024  # 50KB
