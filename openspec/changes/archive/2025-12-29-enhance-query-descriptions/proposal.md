# Change: Enhance Query Descriptions

## Why
在 `app/api/v1/endpoints/resources.py` 中，部分接口（如 `get_donghuan_metric_summary` 和南孜系列接口）的 Query 参数描述较为简略，缺乏详细的中文备注和业务示例，影响了开发者（特别是 AI Agent）对参数含义的理解。

## What Changes
- **MODIFIED**: `app/api/v1/endpoints/resources.py`
    - 为 `list_yunshu_rooms`、`list_yunshu_racks`、`list_yunshu_device_points` 的所有显式 Query 参数添加详细的中文 `description` 和 `examples`。
    - 优化 `get_donghuan_metric_summary` 的参数描述，明确必填项和时间格式。

## Impact
- **影响范围**: 所有资源类接口的 OpenAPI 文档。
- **风险**: 无。
