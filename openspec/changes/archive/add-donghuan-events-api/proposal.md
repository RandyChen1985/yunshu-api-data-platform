# Change: Add Donghuan Events API

## Why
根据 MVP 计划，系统需要提供“动环告警事件”的查询能力，供运维人员和 AI Agent 分析历史告警。
目前 ClickHouse 中已有 `ck_fact_donghuan_event_detail_hbase` 表，但 API 层尚未实现对应接口。

## What Changes
1.  **数据适配**: 在 `ClickHouseAdapter` 中映射动环事件表及相关字段。
2.  **Schema 定义**: 创建 `DonghuanEventResponse` Pydantic 模型。
3.  **API 实现**: 新增 `/api/v1/resources/donghuan/events` 接口，支持按时间、等级、类型、资源ID过滤。
4.  **测试**: 编写配套的集成测试 `tests/api/v1/test_resources_donghuan_events.py` 并更新 `CHECKLIST.md`。

## Impact
-   **Affected Specs**: `resources`
-   **Affected Code**:
    -   `app/api/v1/endpoints/resources.py`
    -   `app/api/v1/schemas/data.py`
    -   `app/services/data_adapter.py`
    -   `tests/` (New test file)
