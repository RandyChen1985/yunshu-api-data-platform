# admin-mgt Specification

## Purpose
TBD - created by archiving change verify-admin-keys. Update Purpose after archive.
## Requirements
### Requirement: API Key Creation
The system MUST allow authorized admins (系统必须允许授权管理员) to create a new API Key for a named user.

#### Scenario: Create Success
- WHEN sending a `POST` request to `/api/v1/keys` with a unique `user_name`
- THEN the response status should be 200
- AND the response body contains plain-text `api_key` and `user_name`
- AND the key works in subsequent requests (via "X-API-Key" header).

#### Scenario: Duplicate User Handling
- WHEN attempting to create a key for an existing `user_name`
- THEN the system should handle the database unique constraint gracefully.

### Requirement: 数据源管理模块 (Data Source Management)
系统必须 (SHALL) 提供数据源管理模块，允许管理员维护外部数据库的连接参数。

#### Scenario: 仅管理员访问
- **WHEN** 用户角色为 `admin`
- **THEN** 在侧边栏显示“数据源管理”菜单。
- **WHEN** 用户角色为 `user`
- **THEN** 隐藏“数据源管理”菜单，且直接访问 API 时返回 403 Forbidden。

#### Scenario: 连通性测试
- **WHEN** 编辑数据源时点击“测试连接”
- **THEN** 系统尝试建立真实连接并返回结果。

### Requirement: 元数据与数据源关联 (Meta-Data Linking)
在创建或编辑资源元数据时，必须 (MUST) 通过下拉选择器关联已定义的数据源。

#### Scenario: 动态数据源列表
- **WHEN** 打开资源编辑页面
- **THEN** “数据源”选项由后端接口动态加载。

### Requirement: Sensitive Data Masking in Data Sources
系统**必须 (MUST)** 在所有外部接口的返回数据中对敏感信息进行脱敏处理，防止敏感元数据泄露。

#### Scenario: 密码脱敏展示
- **Given** 管理员正在查询数据源列表或详情
- **When** 后端返回数据时
- **Then** `password` 字段应被替换为固定掩码（如 `******`）
- **And** 无论数据库中存储的是加密值还是明文，接口均不得直接返回原始敏感值。

