## 1. 基础架构升级
- [ ] 1.1 封装 `useFullscreen` Composable。
- [ ] 1.2 实现 `Resizable` 布局容器，支持 `divider` 拖拽监听。
- [ ] 1.3 重构 `SQLLab.vue` 模板，应用新的响应式高度布局。

## 2. 编辑器增强
- [ ] 2.1 更新 `SqlEditor.vue`，集成 `keymap` 快捷键。
- [ ] 2.2 实现 `getSelectedText` 逻辑，并在运行查询时优先读取选中内容。
- [ ] 2.3 添加“全屏”切换按钮及 UI 状态同步。

## 3. 分析与导出 (Analyst Mode)
- [ ] 3.1 实现多工作表 Excel 导出逻辑（含 SQL 说明页）。
- [ ] 3.2 开发 `AnalysisChat.vue` 组件，集成 Markdown 和 ECharts 渲染。
- [ ] 3.3 后端增加针对导出操作的审计记录 API（写入 `sys_api_audit_log`）。
- [ ] 3.4 在 API 发布逻辑中补全审计记录。
- [ ] 3.5 实现分析按钮和导出按钮的 `v-if` 权限显显逻辑。
- [ ] 3.6 实现模式切换器（右上角）及其状态持久化。

## 4. 审计系统重构
- [ ] 4.1 生成数据库迁移 SQL 文件并保存至 `db-prod/V13-add-audit-action-type.sql`（增加 `action_type` 字段及索引）。
- [ ] 4.2 更新后端通用审计写入逻辑，支持并强制传入 `action_type`。
- [ ] 4.3 升级 `AuditLogs.vue`，增加“功能点”筛选框及表格列展示。
- [ ] 4.4 补全所有已有业务路径的 `action_type` 标记。
