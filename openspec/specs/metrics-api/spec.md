# metrics-api Specification

## Purpose
TBD - created by archiving change allow-multiple-resource-ids-in-metrics. Update Purpose after archive.
## Requirements
### Requirement: Multi-Resource Filtering
The system MUST support filtering by multiple resource IDs via comma-separated strings in metrics APIs.

#### Scenario: Query Multiple Resources
- **WHEN** 发送请求至 `/api/v1/resources/donghuan/real-metrics?resource_id=ID1,ID2`。
- **THEN** 系统应该解析出 `['ID1', 'ID2']`。
- **AND** 使用 `IN` 操作符执行数据库查询。
- **AND** 返回包含这两个资源的所有匹配指标。

#### Scenario: Summary for Multiple Resources
- **WHEN** 请求 `/api/v1/resources/donghuan/real-metrics/summary?resource_id=ID1,ID2`。
- **THEN** 返回的统计数据应覆盖这两个资源的数据总和。

