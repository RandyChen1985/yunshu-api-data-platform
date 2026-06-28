# Spec: Permissions UI

## ADDED Requirements

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
