# CHANGELOG — WB贴图

## v3.1.0 — 2026-06-28

- **3D识别优化**：像素变化检测替代IsHungAppWindow，不等窗口响应直接等画面渲染
- **QT兼容**：美图是QT应用，文件对话框检测兼容#32770和QT弹窗
- **保存重写**：Ctrl+S → 填路径(2200,555) → 填文件名(2180,628) → 设品质(2260,758) → 保存(2224,985)
- **修复双.jpg**：文件名去扩展名粘贴，解决DX0072_B_黑T.jpg.jpg问题
- **窗口标题**：繁简体兼容（美圖秀秀/美图秀秀）
- **启动顺序**：杀进程 → 启动图片编辑 → 定位窗口(1280,0) → 再加载胚衣
- **跳过致命BUG**：发送消息超时(SendMessageTimeout)对QT无效
- **回滚命令**：`git checkout v3.1.0`

## v3.0 (OS重构) — 2026-06-25

- 重构为OS 7层架构（config/core/services/utils/workflow/entrypoint）
- 提取共享Win32 API到services/win32.py
- 提取美图操作到services/meitu.py
- 提取深色检测到utils/detector.py
- 配置集中到config/settings.py
- 向后兼容：旧文件作为存根保留
- **回滚命令**：`git checkout v3.0`

## v2.8.0 — 2026-06-22

- DX0002-DX0034 白T+黑T 全部100%成功
- 黑T深色检测跳过
- **回滚命令**：`git checkout v2.8.0`

## v2.7.0 — 2026-06-21

- 新增胚衣重开流程、白T→黑T顺序规范
- 保存弹窗异常处理（重试2次跳过）
- **回滚命令**：`git checkout v2.7.0`

## v2.6.0 — 2026-06-21

- AI工具坐标(1320,140)、胚衣等待1.5s
- 黑背不旋转、统一TARGET_X=2115
- **回滚命令**：`git checkout v2.6.0`

## v2.5.0 — 2026-06-21

- 速度优化 混合v2+v3
- **回滚命令**：`git checkout v2.5.0`

## v2.4.0 — 2026-06-21

- 轻量验证+拖动加速
- **回滚命令**：`git checkout v2.4.0`

## v2.3.0 — 2026-06-19

- 修复patch破坏的click函数
- 非首次启动也点AI工具
- **回滚命令**：`git checkout v2.3.0`

## v2.2.0 — 2026-06-19

- 保存路径：pyperclip+双重验证+分步Ctrl+V
- **回滚命令**：`git checkout v2.2.0`

## v2.0.0 — 2026-06-16

- 支持白T/黑T双模式，--black参数
- **回滚命令**：`git checkout v2.0.0`
