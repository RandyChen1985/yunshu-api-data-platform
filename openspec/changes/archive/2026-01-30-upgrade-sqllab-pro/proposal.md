# 变更：SQLLab 专业化升级 (Pro Workbench)

## Why
目前的 SQL Lab 仅提供基础的查询和 AI 辅助功能，在处理复杂 SQL 编写、数据探索性分析以及高频操作场景下，易用性和专业度仍有提升空间。引入全屏沉浸模式、可拖拽布局、数据可视化和专业快捷键，能显著提升数据分析师的工作效率。

## What Changes
- **双身份模式切换**：引入“API 调试模式”和“自助取数模式”，根据用户场景动态调整功能集。
- **分析与导出增强**：支持结果集 5000 行 Excel 导出、AI 专家多轮分析（含图表渲染）。
- **工作台交互升级**：全屏工作台模式，支持面板自由拖拽缩放（Resizable Layout）。
- **审计系统重构**：升级 `sys_api_audit_log` 模型，引入“功能点 (Action Type)”维度，支持按“接口服务”、“数据导出”、“API 发布”等业务语义精准查询。
- **权限闭环**：导出、分析、发布均受细粒度权限点控制。

## Impact
- **受影响规格**：`sqllab-pro` (New Capability)
- **受影响代码**：`frontend/src/views/SQLLab.vue` 及其子组件。
- **依赖引入**：`echarts` (或使用现有的 `vue-echarts`), `file-saver`, `xlsx`。
