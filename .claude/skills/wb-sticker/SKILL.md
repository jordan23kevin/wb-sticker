---
name: wb-sticker
description: Use when the user says "wb贴图", "跑贴图", "黑T", "白T", or needs to process T-shirt sticker compositing with Meitu XiuXiu. Handles white/black T-shirt sticker placement automation.
---

# WB贴图 — T恤贴图自动化

## Overview

美图秀秀GUI自动化：去背PNG贴到白T/黑T胚衣上，输出到03_UPLOAD。

## When to Use

- 用户说"wb贴图"、"跑贴图"、"跑黑T"、"跑白T"
- 需要在美图秀秀里批量将去背图贴到T恤模板上
- DX文件夹有02_REM_BG源图但缺03_UPLOAD输出

## Quick Reference

| 命令 | 说明 |
|:------|:-----|
| `python entrypoint/main.py` | 白T全量扫描 |
| `python entrypoint/main.py --black` | 黑T全量扫描 |
| `python entrypoint/main.py DX0001` | 指定文件夹白T |
| `python entrypoint/main.py --black DX0001` | 指定文件夹黑T |

## Core Flow

```
杀进程 → 启动图片编辑 → 定位窗口(1280,0) → 打开胚衣
  → kill_extra_windows → AI工具(1320,140)→AI贴图(1460,560)
  → 新增图片(1510,678) → 导入→等3D(窗口移动检测)
  → 选中贴图(2110,800) → 旋转 → 拖动
  → 混合模式 → Ctrl+S → 填路径(2200,555) → 填文件名(2180,628)
  → 品质(2260,758)→保存(2224,985)
```

## Key Coordinates

美图窗口固定在(1280,0) 1280宽。

| 操作 | 绝对坐标 |
|:-----|:------:|
| AI工具 | (1320, 140) |
| AI贴图 | (1460, 560) |
| 新增图片 | (1510, 678) |
| 选中贴图 | (2110, 800) |
| 旋转 | (2102, 993) |
| 保存-路径 | (2200, 555) |
| 保存-文件名 | (2180, 628) |
| 保存-品质 | (2260, 758) |
| 保存-按钮 | (2224, 985) |

## Critical Rules

1. **先白T后黑T**，全部做完再汇报
2. **复用美图不点AI入口**：已运行时直接点新增图片，失败时才展开AI面板重试
3. **3D检测**：窗口移动1px→回原位，窗口能移动=渲染完成
4. **keep_alive切胚衣**：不杀进程，Ctrl+W关闭→Popen新胚衣
5. **窗口标题**：繁简体兼容(美圖秀秀/美图秀秀)
6. **文件对话框**：QT应用，找#32770类名弹窗
7. **保存文件名去扩展名**：对话框自动加.jpg
8. **黑T审查**：跑完同步到01_CHECK给用户人工审查

## 相关仓库

- `jordan23kevin/wb-sticker` — 贴图脚本
- `jordan23kevin/ps-compositing` — PS合成
