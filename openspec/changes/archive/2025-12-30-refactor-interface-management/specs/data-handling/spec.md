# 数据类型标准化

## ADDED Requirements

### Requirement: 数据类型下拉选择
字段配置中的数据类型输入 MUST be normalized. 目前自由文本输入容易导致错误，应改为下拉选择固定类型。

#### Scenario: 配置字段类型
- **Given** 我正在“接口管理”界面编辑一个资源
- **When** 我在“字段配置”或“允许过滤配置”区域设置“数据类型”列时
- **Then** 系统应显示一个下拉选择框
- **And** 可选值应限制为：`String`, `Long`, `Date`

### Requirement: 数据类型自动标准化逻辑
从数据库导入字段时，系统 MUST automatically map database types. 需要将数据库特定的类型自动映射为系统支持的标准类型。

#### Scenario: 从数据库导入字段
- **Given** 我使用“从数据库导入”功能
- **When** 数据库返回的列类型是 `Nullable(String)` 或类似变体
- **Then** 在配置列表中应自动映射为 `String`
- **And** 其他复杂类型应映射为最接近的标准类型（默认为 `String`）
