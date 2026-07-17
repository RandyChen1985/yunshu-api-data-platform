# nanzi-schema Specification

## Purpose
TBD - created by archiving change complete-nanzi-schemas. Update Purpose after archive.
## Requirements
### Requirement: Full-Field Resource Response
The API MUST return all available columns from the underlying data warehouse tables for NanZi resources (Rooms, Racks, Device Points).

#### Scenario: Complete Room Details
- **WHEN** 查询 `/yunshu/rooms` 接口。
- **THEN** 返回的 JSON 对象必须包含 `jgzs` (机柜总数), `dz` (地址), `bz` (备注) 等全量属性，而不仅仅是基础的编码和名称。

#### Scenario: Complete Rack Details
- **WHEN** 查询 `/yunshu/racks` 接口。
- **THEN** 返回的数据必须包含电力信息（`ac19`, `bzdl`）、PDU 信息（`pdulx`, `apdu`, `bpdu`）以及合同客户信息。

### Requirement: 流控配置项存储
系统必须在 `sys_config` 表中维护流控相关的全局参数（如 `ratelimit.enabled`, `ratelimit.admin.limit`, `ratelimit.user.limit`），并支持在 `api_users` 和 `sys_roles` 表中定义个性化覆盖值。

### Requirement: 多级限流值覆盖 (Hierarchical Overrides)
限流阈值应支持按用户、角色和系统全局三个级别进行配置。优先级顺序为：用户级 -> 角色级 -> 系统全局默认。

#### Scenario: 用户级覆盖生效
- **Given** 全局限流为 100
- **And** 管理员为特定用户 A 设置了专用限流 500
- **When** 用户 A 发起请求
- **Then** 系统应优先采用 500 次/分钟的阈值。

