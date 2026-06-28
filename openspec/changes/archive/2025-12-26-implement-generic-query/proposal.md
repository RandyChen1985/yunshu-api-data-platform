# 提案：通用查询接口 (General Query Interface)

## Why
- **灵活性 (Agility)**: 当前的资源化接口 (`/resources/*`) 无法满足 AI Agent 动态生成查询维度的需求（例如随意组合指标、时间粒度）。
- **解耦 (Decoupling)**: 降低后端为每个新报表开发 Dedicated API 的工作量。
- **架构一致性 (Architecture)**: 符合 `API_SERVICE_DETAILED_DESIGN.md` 中 3.1.2 节关于“通用查询接口”的规划。

## What Changes
- **新增接口**: `POST /api/v1/query`，接收 `LogicalQuery` 结构。
- **路由实现**: 挂载 `app/api/v1/endpoints/query.py`。
- **核心逻辑**:
  - 绑定 ClickHouse 适配器 (`DataSourceAdapter`).
  - 实现通用查询的分页、排序、过滤处理。
  - **安全增强**: 校验 `resource` 合法性（白名单），防止任意 SQL 注入。

## Risks
- **SQL 注入风险**: 虽然通过 Adapter 抽象，但如果过滤条件或排序字段处理不当，仍有风险。需严格校验字段白名单。
- **性能风险**: 开放随意组合查询可能导致慢查询。需依赖 ClickHouse 的资源配额或在 Adapter 层增加超时限制。
