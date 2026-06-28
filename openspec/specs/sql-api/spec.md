# sql-api Specification

## Purpose
该规格说明书旨在定义动态 SQL 执行接口的标准行为，包括参数化查询、结果集格式化、权限控制、审计日志记录以及基础的 SQL 安全校验逻辑。它是系统提供灵活数据查询能力的核心组件。
## Requirements
### Requirement: The system MUST provide a generic API endpoint for executing raw SQL queries.
该接口**必须 (MUST)** 作为通用 SQL 执行通道，支持 ChatBI 及其他 AD-HOC 查询场景。

#### Scenario: 成功执行合法的 SELECT 查询
Given 一个指向活跃数据源的有效 `data_source_id`
And 一个原生 SQL 字符串 "SELECT * FROM my_table WHERE id = %(id)s"
And 一个参数字典 `{"id": 1}`
When 向 `/api/v1/sql/execute` 发送 POST 请求，包含上述参数
And 请求包含有效的 API Key 和 `system.sql.execute` 权限
Then 系统应在指定数据源上执行该查询
And 以 JSON 格式返回结果，包含 "columns" (字段名及类型) 和 "items" (数据行)
And 返回 200 OK 状态码。

### Requirement: The endpoint MUST be grouped under the "General Query" tag in documentation.
在 API 文档中，该接口**必须 (MUST)** 显示在 "通用查询" 分类下，名称为 "动态 SQL 查询"，并包含详细的使用说明。

#### Scenario: 检查文档属性
Given 生成的 OpenAPI Schema
When 检查 `/api/v1/sql/execute` 路径
Then 它的 `tags` 列表应包含 "通用查询"
And 它的 `summary` 应为 "动态 SQL 查询"。

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

### Requirement: The system MUST record audit logs for every execution.
为了追溯 SQL 执行行为，系统**必须 (MUST)** 记录包含用户、SQL及状态的详细日志。

#### Scenario: 记录成功日志
Given 一个成功的 SQL 执行请求
Then 系统应将 execution metadata (user, sql, time, status) 写入审计日志存储。

### Requirement: The system MUST automatically enforce row limits.
为了防止过载，系统**必须 (MUST)** 检测并强制追加 LIMIT 子句。

#### Scenario: 自动强制追加 LIMIT
Given 一个不包含 LIMIT 子句的查询 "SELECT * FROM large_table"
When 执行该查询
Then 系统应在执行前向 SQL 追加默认的行数限制 (如 LIMIT 1000)
Or 在返回结果时截断超过限制的行数。

### Requirement: DataSourceAdapter interface MUST support raw SQL execution with parameters.
适配器接口**必须 (MUST)** 扩展以支持执行原始 SQL 字符串，并接收可选的参数字典。

#### Scenario: 抽象方法定义
Given `DataSourceAdapter` 抽象基类
When 检查其方法列表
Then 它应包含一个抽象方法 `execute_sql(self, sql: str, params: Dict[str, Any] = None) -> Dict[str, Any]`。

### Requirement: Robust SQL Validation using AST
系统**必须 (MUST)** 使用专业的 SQL 解析库对原生 SQL 进行深度检查，严格限制仅允许执行非破坏性的查询语句。

#### Scenario: AST 解析验证
- **Given** 一个原始 SQL 字符串
- **When** 提交执行前
- **Then** 系统应使用 `sqlparse` 等工具解析语句结构
- **And** 验证语句类型必须为 `SELECT`（或 `WITH ... SELECT`）
- **And** 拒绝任何包含数据修改（DML）、结构修改（DDL）或权限控制（DCL）的非法请求。
- **And** 报错信息应明确指出“仅支持 SELECT 查询”。

