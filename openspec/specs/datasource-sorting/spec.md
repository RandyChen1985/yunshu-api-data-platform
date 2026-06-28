# datasource-sorting Specification

## Purpose
TBD - created by archiving change datasource-drag-sort. Update Purpose after archive.
## Requirements
### Requirement: 数据源列表按自定义权重排序
系统 SHALL 在获取数据源列表时，优先按照 `sort_order` 升序排序，次要按照 `id` 降序排序。

#### Scenario: 验证列表排序
- **WHEN** 用户访问数据源管理页面或 SQL Lab 数据源下拉框
- **THEN** 系统返回的数据源顺序必须遵循 `sort_order` 升序规则

### Requirement: 支持通过拖拽重新排列数据源顺序
系统 SHALL 允许具有编辑权限的用户在数据源管理页面通过拖拽操作改变数据源位置。

#### Scenario: 拖拽保存排序
- **WHEN** 用户将列表中的第 3 项拖拽到第 1 项的位置
- **THEN** 前端 SHALL 调用批量更新接口发送新的 ID 序列
- **AND** 系统 SHALL 持久化新的排序权重，并提示“排序更新成功”

### Requirement: 数据源批量排序 API
系统 SHALL 提供一个接口，接受数据源 ID 的序列，并根据该序列原子化地更新所有涉及数据源的 `sort_order`。

#### Scenario: 成功调用排序接口
- **WHEN** 发送 `PUT /api/portal/datasource/datasources/reorder` 请求，Payload 为 `{"ids": [5, 2, 8]}`
- **THEN** ID 为 5 的记录 `sort_order` 变为 0，ID 为 2 的变为 1，ID 为 8 的变为 2

