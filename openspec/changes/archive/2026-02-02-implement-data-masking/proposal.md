## Why

当前系统在返回数据时直接透传数据库中的明文信息，存在敏感数据（如手机号、邮箱、身份证等）泄露的风险。为了满足安全合规需求，需要建立一套灵活的、基于配置的动态脱敏系统，并支持全局、角色、用户三级覆盖策略。

## What Changes

- **数据库扩展**：
    - 新增 `sys_masking_rules` 表，用于存储脱敏字段规则。
    - 扩展 `sys_roles` 表，增加 `masking_strategy` 字段。
    - 扩展 `sys_users` 表，增加 `masking_strategy` 字段。
- **后端服务**：
    - 实现 `MaskingService`：负责递归扫描响应数据并应用脱敏算法，同时实现三级覆盖策略判定逻辑。
    - 权限集成：根据当前用户的三级配置自动判定是否应用脱敏（Admin 默认拥有豁免权或可通过参数查看明文）。
- **前端界面**：
    - **系统设置**：新增“数据脱敏”标签页，支持规则 CRUD 和全局总开关。
    - **角色管理**：编辑角色时支持设置脱敏策略（跟随全局/强制开启/允许明文）。
    - **用户管理**：编辑用户时支持设置脱敏策略（跟随角色/强制开启/允许明文）。

## Capabilities

### New Capabilities
- `data-masking`: 核心脱敏引擎，支持对 API 响应数据的自动扫描与打码逻辑。
- `masking-management`: 管理后台功能，支持三级（全局、角色、用户）脱敏策略的动态配置。

### Modified Capabilities
- `resource-access`: 资源查询接口集成脱敏处理器。
- `user-management`: 用户管理支持脱敏策略设置。
- `role-management`: 角色管理支持脱敏策略设置。

## Impact

- **API 接口**：`/api/v1/resources/*` 和 `/api/portal/lab/execute`。
- **管理后台**：`/api/portal/system/`, `/api/portal/management/`, `/api/portal/roles/`。
- **数据库**：多表结构变更。