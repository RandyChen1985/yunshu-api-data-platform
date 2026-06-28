## MODIFIED Requirements
### Requirement: The system MUST enforce 'system.sql.execute' permission for the endpoint.
接口**必须 (MUST)** 集成到现有的用户权限管理体系中，确保只有授权用户访问，且必须校验具体的数据源和表权限。校验遵循“显式授权”原则。

#### Scenario: 验证权限 (显式全通 = ALL)
Given 一个拥有以下权限的用户:
    - `system.sql.execute`
    - `ds:clickhouse-prod`
    - `ds:clickhouse-prod:table:*` (显式全通)
When 该用户请求在 `clickhouse-prod` 上查询 `SELECT * FROM any_random_table`
Then 允许通过。

#### Scenario: 验证权限 (具体表白名单)
Given 一个拥有以下权限的用户:
    - `system.sql.execute`
    - `ds:clickhouse-prod`
    - `ds:clickhouse-prod:table:users` (仅 users)
When 该用户请求查询 `SELECT * FROM users`
Then 允许通过。

#### Scenario: 拒绝访问未授权的表
Given 上述用户 (仅有 users 权限)
When 该用户请求查询 `SELECT * FROM orders`
Then 系统应拒绝请求 (403)。

#### Scenario: 拒绝未配置表权限的用户 (空 = 无权限)
Given 一个拥有以下权限的用户:
    - `system.sql.execute`
    - `ds:clickhouse-prod`
    - (无任何 table 权限，也没配 *)
When 该用户请求在 `clickhouse-prod` 上查询任何表
Then 系统应拒绝请求 (403)。