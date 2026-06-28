## 上下文
SQL Lab 是平台高频使用的核心模块。现有的 Vue 结构采用固定的 `flex-col` 布局，高度受限于视口且不可调节。

## 目标
- 实现响应式、可调节的工作台布局。
- 保证在全屏状态下功能的完整性。
- 引入智能数据探索能力。

## 技术决策
- **全屏实现**：封装 `useFullscreen` composable，监听 `fullscreenchange` 事件同步 UI 状态。
- **模式管理**：使用 `localStorage` 持久化用户选择的 `lab_mode` (api/analyst)。
- **AI 角色 (Persona)**：
    - `api` 模式：开发者角色，执行严格 SQL 审计和参数化生成。
    - `analyst` 模式：运营专家角色，侧重业务洞察，生成逻辑最简 SQL。
- **分析对话框**：
    - 状态管理：使用响应式 Ref 维护消息流，**会话不进行持久化**，关闭窗口或重新执行 SQL 后立即清空。
    - 渲染器：开发 `ChatContentRenderer`，支持 Markdown 和基于 JSON 块的 ECharts 动态渲染。
- **数据处理**：AI 分析请求将包含 `current_sql` 和全量结果集。
- **导出能力**：利用 `xlsx` 导出多 Sheet 文档。前端限制最大处理 **5000 行**数据以保证性能。
- **权限集成**：由管理员手动配置 `element:lab:export` 和 `element:lab:analysis`。
- **审计系统重构**：
    - **Schema 变更**：`sys_api_audit_log` 增加 `action_type` 字段（索引优化）。
    - **功能点枚举 (Action Types)**：
    - **SQL 实验室**：`LAB_QUERY`, `LAB_EXPORT`, `LAB_ANALYSIS`, `LAB_PUBLISH`, `LAB_METADATA`。
    - **数据服务**：`API_QUERY`, `SQL_EXECUTE`。
    - **系统管理**：`DS_EDIT`, `RES_EDIT`, `USER_MANAGE`, `CONFIG_SAVE`。
    - **查询增强**：`GET /api/portal/audit/logs` 增加 `action_type` 过滤参数。

## 风险与权衡
- **结果集数据传输**：AI 分析需要结果集上下文。对于特大数据量，实施 2000 行截断保护。

## 风险与权衡
- **图表性能**：万级以上数据在前端绘图可能卡顿。
    - *缓解*：图表仅针对预览结果（Top 100/500）进行绘制。
- **布局冲突**：全屏下某些 CSS 固定定位（fixed）的全局 Toast 或 Modal 可能会被遮挡。
    - *缓解*：确保所有弹窗挂载在全屏容器内部或提高 `z-index`。

## 待定问题
- 是否需要支持多个图表并排显示？
- 导出功能是否由后端直接生成文件（以支持全量数据导出）？
