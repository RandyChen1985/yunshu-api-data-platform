# sqllab-pro Specification

## Purpose
该规格定义了 SQL 实验室的高级工作台功能，旨在为用户提供高效、沉浸且具备数据探索能力的 SQL 编写与分析环境。

## ADDED Requirements
### Requirement: Immersive Fullscreen Mode
系统**必须 (MUST)** 提供全屏切换功能，使 SQL 实验室占据整个浏览器视口。

#### Scenario: 进入全屏
- **WHEN** 用户点击工具栏的“全屏”按钮
- **THEN** 系统利用 Fullscreen API 放大工作区
- **AND** 隐藏系统侧边导航和顶栏
- **AND** 自动调整内部面板高度以填充屏幕。

#### Scenario: 退出全屏
- **WHEN** 用户按下 ESC 键或点击“退出全屏”按钮
- **THEN** 系统恢复原始布局和系统导航。

### Requirement: Draggable Layout Resizing
工作台各面板之间**必须 (MUST)** 支持手动拖拽调整大小。

#### Scenario: 调整编辑区高度
- **WHEN** 用户上下拖拽编辑器与结果面板之间的分割线
- **THEN** 编辑器高度随之增减，结果面板占据剩余空间。

### Requirement: Keyboard-First Navigation
编辑器**必须 (MUST)** 支持行业标准的 SQL 快捷键。

#### Scenario: 运行 SQL
- **WHEN** 用户按下 `Ctrl + Enter` (或 `Cmd + Enter`)
- **THEN** 系统立即执行当前 Tab 或选中的 SQL。

### Requirement: Dual-Mode Operation (API vs Analyst)
系统**必须 (MUST)** 支持“API 调试”与“自助取数”模式切换。

#### Scenario: 切换至自助取数模式
- **WHEN** 用户选择“自助取数”
- **THEN** 系统隐藏 `Publish API`, `AI Check` 等开发向按钮
- **AND** AI 生成 SQL 时不再强制执行参数化校验。

### Requirement: Interactive AI Data Analysis
系统**必须 (MUST)** 支持针对结果集进行多轮 AI 分析，且每次分析均为独立会话。

#### Scenario: 运营专家对话
- **GIVEN** 已获得查询结果
- **WHEN** 用户点击“AI 智能分析”
- **THEN** 弹出对话窗口，系统将 SQL 及数据发送给 AI
- **AND** 关闭窗口后会话自动销毁。

### Requirement: Comprehensive Audit Logging
系统**必须 (MUST)** 对所有可能导致数据泄露或配置变更的操作进行审计。

#### Scenario: 审计导出行为
- **WHEN** 用户执行导出 Excel 操作
- **THEN** 系统自动在 `sys_api_audit_log` 记录该行为，且 `action_type` 设置为 `LAB_EXPORT`。

#### Scenario: 审计发布行为
- **WHEN** 用户点击“确认发布” API
- **THEN** 系统记录该行为，且 `action_type` 设置为 `LAB_PUBLISH`。
