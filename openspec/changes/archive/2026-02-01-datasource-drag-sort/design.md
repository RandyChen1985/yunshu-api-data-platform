## Context

目前 `sys_data_source` 表缺乏显式的排序权重字段，导致列表展示顺序依赖于数据库默认排序（通常是 `id`）。为了提升用户体验，需要引入一种机制让用户可以自定义排序顺序。

## Goals / Non-Goals

**Goals:**
- 在 `sys_data_source` 表中持久化排序权重。
- 提供批量更新排序的 API。
- 在前端管理页面支持拖拽排序，并实时保存。
- 确保全局数据源获取接口遵循该排序规则。

**Non-Goals:**
- 不涉及数据源的其他属性变更（如连接参数）。
- 不涉及自动化性能监控或健康检查排序。

## Decisions

### 1. 数据库字段设计
- **方案**: 在 `sys_data_source` 新增 `sort_order` 字段，类型为 `INT`，默认值为 0。
- **理由**: 简单直接，易于在查询时使用 `ORDER BY`。默认值为 0 意味着新创建的数据源会排在前面（如果按升序排）或通过 ID 辅助排序。

### 2. 后端 API 设计
- **新增接口**: `PUT /api/portal/datasource/datasources/reorder`
- **Payload**: `{ "ids": [3, 1, 2] }`
- **处理逻辑**: 后端按数组顺序，将 `sort_order` 分别设置为 `0, 1, 2...`。
- **理由**: 批量更新比逐个更新效率更高，前端只需传递最终的 ID 序列。

### 3. 前端实现
- **库选择**: `vuedraggable` (基于 Sortable.js)。
- **交互**: 在 `DataSourceList.vue` 的表格中使用，拖拽结束后触发 `reorder` API。

## Risks / Trade-offs

- **[Risk] 并发排序冲突** → **[Mitigation]** 由于这是管理类操作，冲突概率低。采用全量 ID 列表覆盖式更新排序权重。
- **[Trade-off] 性能** → 数据源数量通常在几十个以内，全量更新 `sort_order` 的性能开销极小。

## Migration Plan

1. 执行 SQL 脚本，在 `sys_data_source` 中添加 `sort_order` 字段。
2. 初始化现有数据的 `sort_order`（可按 `id` 顺序填充）。
3. 部署后端更新，引入 `reorder` 接口并修改 `list` 接口排序逻辑。
4. 部署前端代码。
