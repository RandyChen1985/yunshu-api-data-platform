## Why

当前数据源列表（DataSourceList）以及 SQL Lab 中的数据源下拉列表是无序的（通常按创建时间或 ID 排序）。随着数据源数量增加，用户难以快速找到常用数据源。支持拖拽排序可以显著提升用户在管理页面和 SQL 查询时的效率。

## What Changes

1.  **数据库层**：在 `sys_data_source` 表中新增 `sort_order` 字段（整数类型），默认为 0。
2.  **API 层**：
    *   修改 `GET /api/portal/datasource/datasources` 接口，默认按 `sort_order` 升序、`id` 降序排列。
    *   新增 `PUT /api/portal/datasource/datasources/reorder` 接口，支持批量更新数据源的排序权重。
3.  **前端 UI**：
    *   在 `DataSourceList.vue` 列表中引入 `vuedraggable` 或类似库，实现拖拽交互。
    *   拖拽完成后自动触发排序更新请求。
    *   确保 SQL Lab 等其他引用数据源列表的地方也遵循新的排序规则。

## Capabilities

### New Capabilities
- `datasource-sorting`: 实现数据源列表的自定义排序能力，包括后端字段存储、批量排序接口和前端拖拽交互。

### Modified Capabilities
- (无)

## Impact

- **Database**: `sys_data_source` 表结构变更。
- **Backend**: `DataSourceService` 和相关的 API 路由。
- **Frontend**: `DataSourceList.vue` 页面交互逻辑；`SQLLab.vue` 数据获取展示顺序。
