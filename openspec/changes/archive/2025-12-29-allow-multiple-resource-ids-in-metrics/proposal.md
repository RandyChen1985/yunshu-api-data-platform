# Change: Allow Multiple Resource IDs in Metrics API

## Why
目前动环实时指标相关接口仅支持单个 `resource_id` 查询。为了支持更复杂的监控看板和批量数据获取需求（如同时查看多个 UPS 的实时电压），需要支持通过逗号分隔的方式传入多个 `resource_id`。

## What Changes
- **MODIFIED**: `app/api/v1/endpoints/resources.py`
    - 修改 `list_donghuan_real_metrics` 逻辑：解析 `params.resource_id`，如果包含逗号，则使用 `IN` 操作符进行过滤。
    - 修改 `get_donghuan_metric_summary` 逻辑：同上。
- **MODIFIED**: `app/api/v1/schemas/data.py`
    - 增强 `DataQueryParams` 中 `resource_id` 的描述，说明支持逗号分隔。

## Impact
- 影响组件：动环实时指标查询、指标统计汇总。
- 向后兼容：单个 ID 查询逻辑保持不变。
