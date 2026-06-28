# interface-management Specification

## Purpose
TBD - created by archiving change refactor-interface-management. Update Purpose after archive.
## Requirements
### Requirement: 模块标题更新
为了更符合业务语义，系统 MUST change the module name. 需要将模块名称从技术性的“元数据配置”更改为“接口管理”。

#### Scenario: 访问模块
- **Given** 我登录并处于控制台仪表盘
- **When** 我进入资源列表页面
- **Then** 页面顶部的标题应显示为“接口管理”
- **And** 不应再看到“元数据配置”字样

### Requirement: 资源列表备注提示
用户需要在不进入详情页的情况下快速查看资源的用途描述，The UI MUST provide tooltips.

#### Scenario: 查看资源备注
- **Given** 我正在查看资源列表
- **And** 某个资源的“备注”字段有内容
- **When** 我将鼠标悬停在该资源的名称上
- **Then** 应弹出一个提示框（Tooltip）显示备注的完整内容
- **And** 提示框的样式应与编辑页面的样式保持一致

### Requirement: 状态过滤功能
资源列表 MUST support filtering by status. 应支持按“状态”进行筛选，以便管理员快速查看启用或禁用的接口。

#### Scenario: 按状态筛选
- **Given** 我在资源列表页面
- **When** 我在搜索栏旁边的状态过滤器中选择“启用”
- **Then** 列表应只显示状态为 1 (启用) 的资源
- **When** 我选择“禁用”
- **Then** 列表应只显示状态为 0 (禁用) 的资源

### Requirement: 资源配置导出
系统 MUST allow exporting resource configuration. 用户可以将单个资源的完整配置（不含敏感连接信息，但包含SQL/字段配置）导出为 JSON 文件，用于备份或迁移。

#### Scenario: 导出配置
- **Given** 我在资源列表页面
- **When** 我点击某一行资源的“导出”按钮
- **Then** 浏览器应下载一个 JSON 文件
- **And** 文件内容应包含该资源的所有配置字段（Resource Name, Group, Mode, SQL/Table, Fields, Filters 等）

### Requirement: 资源配置导入
系统 MUST allow importing resource configuration. 用户可以上传之前导出的 JSON 文件，系统解析后跳转到“新建资源”页面并自动填充表单。

#### Scenario: 导入配置
- **Given** 我在资源列表页面
- **When** 我点击“新建资源”旁边的“导入配置”按钮
- **And** 我选择了一个有效的资源配置 JSON 文件
- **Then** 页面应跳转到“新建资源”页面
- **And** 表单的所有字段（除了 Resource Key 可能需要重置或校验唯一性）应自动填充为 JSON 中的值
- **And** 用户可以在保存前修改这些内容

