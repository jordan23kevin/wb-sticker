# WB贴图 架构文档

> 版本: v3.0 (OS) — 2026-06-25
> 架构: Engineering OS 7层

## 结构

```
entrypoint/main.py   → CLI入口
workflow/pipeline.py  → 扫描DX→背→正流水线
core/back.py          → 背图贴图（尾数1）
core/front.py         → 正图贴图（尾数2）
services/meitu.py     → 美图秀秀窗口操作
services/win32.py     → Win32 API封装
utils/detector.py     → 深色检测、偏移计算
utils/sticker_typer.py → 文件名类型判断
config/settings.py    → 坐标、路径、阈值
```

## 依赖方向

entrypoint → workflow → core → services + utils → config

## 核心流程

1. 扫描 `D:\Semems\1AI\DX*` 文件夹
2. 黑T深色预检（有深色则整组跳过）
3. 逐文件夹：背图处理 → 正图处理
4. 美图秀秀：打开胚衣 → AI贴图 → 导入PNG → 旋转拖动 → 混合 → 保存
