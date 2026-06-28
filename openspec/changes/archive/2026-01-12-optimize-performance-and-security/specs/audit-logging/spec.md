# audit-logging Specification Delta

## MODIFIED Requirements

### Requirement: Asynchronous Logging
系统**必须 (MUST)** 采用非阻塞方式记录审计日志，以确保日志写入操作不影响主业务接口的响应时间。

#### Scenario: Background Task Execution
- **GIVEN** 一个进入系统的 API 请求
- **WHEN** 业务逻辑处理完成并准备返回响应时
- **THEN** 系统应启动一个后台任务（如 FastAPI BackgroundTasks）异步执行数据库写入操作
- **AND** 接口应立即返回响应，无需等待日志写入完成。
