# sql-api Specification Delta

## RENAMED Requirements
- FROM: `### Requirement: The system MUST validate SQL for syntax, robustness, and safety.`
- TO: `### Requirement: Robust SQL Validation using AST`

## MODIFIED Requirements

### Requirement: Robust SQL Validation using AST
系统**必须 (MUST)** 使用专业的 SQL 解析库对原生 SQL 进行深度检查，严格限制仅允许执行非破坏性的查询语句。

#### Scenario: AST 解析验证
- **Given** 一个原始 SQL 字符串
- **When** 提交执行前
- **Then** 系统应使用 `sqlparse` 等工具解析语句结构
- **And** 验证语句类型必须为 `SELECT`（或 `WITH ... SELECT`）
- **And** 拒绝任何包含数据修改（DML）、结构修改（DDL）或权限控制（DCL）的非法请求。
- **And** 报错信息应明确指出“仅支持 SELECT 查询”。
