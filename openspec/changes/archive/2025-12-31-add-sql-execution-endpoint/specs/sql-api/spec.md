# 通用 SQL 执行 API & Adapter 扩展

## ADDED Requirements

### Requirement: The system MUST provide a generic API endpoint for executing raw SQL queries.
该接口将作为通用 SQL 执行通道，支持 ChatBI 及其他 AD-HOC 查询场景。

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
在 API 文档中，该接口应显示在 "通用查询" 分类下，名称为 "动态 SQL 查询"，并包含详细的使用说明。

#### Scenario: 检查文档属性
Given 生成的 OpenAPI Schema
When 检查 `/api/v1/sql/execute` 路径
Then 它的 `tags` 列表应包含 "通用查询"
And 它的 `summary` 应为 "动态 SQL 查询"。

### Requirement: The system MUST enforce 'system.sql.execute' permission for the endpoint.
接口必须集成到现有的用户权限管理体系中，确保只有授权用户访问。

#### Scenario: 验证权限
Given 一个拥有 `system.sql.execute` 资源权限的用户
When 该用户请求接口
Then 允许通过。

#### Scenario: 拒绝无权限用户
Given 一个没有 `system.sql.execute` 资源权限的用户
When 该用户请求接口
Then 系统应拒绝请求
And 返回 403 Forbidden 错误。

### Requirement: The system MUST record audit logs for every execution.
为了追溯 SQL 执行行为，系统必须记录包含用户、SQL及状态的详细日志。

#### Scenario: 记录成功日志
Given 一个成功的 SQL 执行请求
Then 系统应将 execution metadata (user, sql, time, status) 写入审计日志存储。

### Requirement: The system MUST automatically enforce row limits.
为了防止过载，系统必须检测并强制追加 LIMIT 子句。

#### Scenario: 自动强制追加 LIMIT
Given 一个不包含 LIMIT 子句的查询 "SELECT * FROM large_table"
When 执行该查询
Then 系统应在执行前向 SQL 追加默认的行数限制 (如 LIMIT 1000)
Or 在返回结果时截断超过限制的行数。

### Requirement: The system MUST validate SQL for syntax, robustness, and safety.
系统必须对 SQL 进行预检查，确保语法正确且不包含破坏性语句。

#### Scenario: 拒绝破坏性语句
Given 一个包含 "DROP TABLE" 的 SQL
When 提交执行
Then 系统应拒绝并返回 400 错误。

#### Scenario: 语法错误处理
Given 一个语法错误的 SQL
When 提交执行
Then 系统应捕获异常并返回友好的错误提示，而不是 500 崩溃。

### Requirement: DataSourceAdapter interface MUST support raw SQL execution with parameters.
适配器接口必须扩展以支持执行原始 SQL 字符串，并接收可选的参数字典。

#### Scenario: 抽象方法定义
Given `DataSourceAdapter` 抽象基类
When 检查其方法列表
Then 它应包含一个抽象方法 `execute_sql(self, sql: str, params: Dict[str, Any] = None) -> Dict[str, Any]`。
