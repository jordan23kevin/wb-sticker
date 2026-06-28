# WB贴图 v3.0 (OS)

通过美图秀秀自动将设计图贴到胚衣（白T/黑T）的 RPA 工具。

## 快速开始

```bash
cd WB\ 贴图
pip install -r requirements.txt

# 白T自动扫描
python entrypoint/main.py

# 黑T自动扫描
python entrypoint/main.py --black

# 指定文件夹
python entrypoint/main.py DX0001
python entrypoint/main.py --black DX0001
```

## 架构

```
WB 贴图/
├── config/          → 配置（坐标、路径、阈值）
├── core/            → 核心逻辑（back.py / front.py）
├── services/        → 美图秀秀操作 + Win32 API
├── utils/           → 图像检测 + 文件名解析
├── workflow/        → 流程编排（扫描DX → 背 → 正）
├── entrypoint/      → 入口
└── docs/            → README / ARCHITECTURE / CHANGELOG
```

## 规则

- 命名：B=背, W=正, BW/WB=先背后正
- 黑T：预检所有PNG，一张过暗(<80)则整组跳过
- 增量保存：不覆盖已有文件
