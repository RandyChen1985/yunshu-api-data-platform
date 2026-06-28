# Proposal: 实现对外接口服务 (/api/v1) 的流控功能

## 1. 动机 (Why)
目前系统的 `/api/v1` 对外接口缺乏实际生效的流控机制，虽然文档中声明了流控策略，但代码实现中仅有未挂载的占位函数。为了保障系统的高可用性，防止接口被滥用，需要实现一套基于 Redis 的动态流控系统，并提供 UI 界面进行配置。

## 2. 目标 (How)
- **后端实现**：
  - 重构 `app/core/dependencies.py` 中的 `check_rate_limit`。
  - **多级覆盖逻辑**：限流值读取顺序为：用户特定配置 -> 角色配置 -> 系统全局配置。
  - **响应头告知**：在 HTTP Header 中增加 `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`。
  - **故障回退 (Fail-Open)**：若 Redis 故障，流控逻辑应自动降级跳过，确保业务不中断。
- **配置管理**：
  - 在 `api_users` 和 `sys_roles` 表中增加流控参数字段。
  - 扩展用户管理和角色管理界面，支持直接配置限流值。
- **配置管理 (系统级)**：
  - 在 `sys_config` 表中增加流控相关的配置项：`ratelimit.enabled`, `ratelimit.admin.limit`, `ratelimit.user.limit`。
  - 管理后台提供 API 动态读写这些配置。
  - **新增统计支持**：提供最近 24 小时分时的分钟级请求峰值查询 API。
- **前端实现**：
  - 在 `SystemConfig.vue` 中增加“流控配置” Tab 页。
  - 实现流控参数的可视化修改与保存。
  - **新增监控卡片**：展示最近 24 小时请求峰值分布图表。

## 3. 设计摘要 (Rationale)
- **动态性**：配置存储在 MySQL `sys_config` 表中，后端在执行流控检查时优先从 Redis 缓存获取配置，若缓存失效则回源数据库，确保修改即时生效且性能损耗极低。
- **数据驱动决策**：通过展示历史峰值请求数据，使管理员能够根据实际业务压力（而非凭空猜测）设定限流策略，平衡安全与可用性。
- **一致性**：复用现有的 `dependencies.py` 结构，保持代码风格统一。
- **安全性**：流控逻辑在 `require_api_key` 之后执行，确保基于已校验的 `user_id` 进行计数。

## 4. 影响范围
- `app/core/dependencies.py`: 修改流控函数逻辑。
- `app/api/v1/endpoints/*.py`: 挂载流控依赖。
- `frontend/src/views/SystemConfig.vue`: 增加配置界面。
- `db-prod/`: 增加初始化 SQL 以注入默认配置项。
