## ADDED Requirements
### Requirement: SQL 安全执行 (SQL Security Execution)
所有 SQL 类型的适配器（如 ClickHouse）必须 (MUST) 使用参数化查询 (Parameterized Queries) 或驱动级参数绑定来防止 SQL 注入。

#### Scenario: 禁止手动拼接
- **WHEN** 执行带有用户输入的过滤条件查询
- **THEN** 适配器通过 `{param}` 或 `%s` 占位符传递参数
- **AND** 不直接在 SQL 字符串中进行值的拼接。

#### Scenario: 操作符支持
- **WHEN** 过滤条件包含 `>`, `<`, `=`, `!=`, `IN` 等操作符
- **THEN** 生成的 SQL 正确包含相应操作符且参数被安全绑定。
