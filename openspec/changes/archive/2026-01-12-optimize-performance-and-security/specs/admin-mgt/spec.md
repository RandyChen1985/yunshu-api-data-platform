# admin-mgt Specification Delta

## MODIFIED Requirements

### Requirement: Sensitive Data Masking in Data Sources
系统**必须 (MUST)** 在所有外部接口的返回数据中对敏感信息进行脱敏处理，防止敏感元数据泄露。

#### Scenario: 密码脱敏展示
- **Given** 管理员正在查询数据源列表或详情
- **When** 后端返回数据时
- **Then** `password` 字段应被替换为固定掩码（如 `******`）
- **And** 无论数据库中存储的是加密值还是明文，接口均不得直接返回原始敏感值。
