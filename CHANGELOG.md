# CHANGELOG — WB贴图

## v3.0 (OS重构) — 2026-06-25

- 重构为OS 7层架构（config/core/services/utils/workflow/entrypoint）
- 提取共享Win32 API到services/win32.py
- 提取美图操作到services/meitu.py
- 提取深色检测到utils/detector.py
- 配置集中到config/settings.py
- 向后兼容：旧文件作为存根保留

## v2.8.0 — 2026-06-22

- DX0002-DX0034 白T+黑T 全部100%成功
