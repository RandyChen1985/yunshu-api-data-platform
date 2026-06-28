## ADDED Requirements
### Requirement: “我的权限”弹窗必须列出数据源和数据表权限
弹窗**必须 (MUST)** 在 API 资源之外，同时列出用户可访问的数据源和数据表。

#### Scenario: 查看数据源权限
- **WHEN** 我打开“我的权限”弹窗
- **THEN** 我应该看到一个“数据源”板块或列表项，展示我有权访问的数据源（例如："clickhouse-prod"）
- **AND** 我应该看到一个“数据表”板块或列表项，展示我有权访问的具体表（例如："users"）

### Requirement: 角色管理界面必须支持数据资产权限分配
管理员**必须 (MUST)** 能够通过图形化界面为角色分配数据源和数据表权限。

#### Scenario: 分配数据源权限
- **GIVEN** 我在编辑一个角色
- **WHEN** 我切换到“数据资产”页签并勾选 "clickhouse-prod"
- **THEN** 保存后，该角色的用户应获得该数据源的访问权限。

#### Scenario: 分配数据表白名单
- **GIVEN** 我已勾选 "clickhouse-prod"
- **WHEN** 我点击“配置表权限”并勾选 "users" 表
- **THEN** 保存后，该角色的用户在 "clickhouse-prod" 下将**只能**访问 "users" 表，无法访问其他表。
