# permissions-ui Specification

## Purpose
TBD - created by archiving change add-my-permissions-feature. Update Purpose after archive.
## Requirements
### Requirement: Dashboard Header - My Permissions Entry
The dashboard header MUST display a "My Permissions" button showing the count of accessible resources.

#### Scenario: User checks dashboard header
Given I am logged in as a normal user with permissions to 9 resources
When I view the dashboard header
Then I should see a "我的权限(9)" button to the left of "Online Users"
And clicking it should open the "My Resources" permission modal

### Requirement: My Resources Modal Resource List
The modal MUST list all resources the user has permission to access, including their ID and basic actions.

#### Scenario: Viewing resource list
Given the "My Resources" modal is open
And I have permission to "donghuan_real_metrics"
Then I should see a card for "动环实时指标"
And the card should display the resource ID "donghuan_real_metrics"
And I should see a copy icon next to the ID

### Requirement: Resource Details Popover
The user MUST be able to view detailed field configuration for each resource.

#### Scenario: Viewing resource details
Given I am viewing the "动环实时指标" card
When I click "字段详情"
Then a popover should appear listing all fields (name, description, type) for that resource

### Requirement: Call Examples Modal
The user MUST be able to view and copy code examples for accessing the resource.

#### Scenario: Viewing call examples
Given I am viewing the "动环实时指标" card
When I click "调用示例"
Then a modal should open with two tabs: "通用调用" and "直接调用"
And "通用调用" tab should show a curl example for `/api/v1/query`
And "直接调用" tab should show a curl example for `/api/v1/resources/donghuan_real_metrics`

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

