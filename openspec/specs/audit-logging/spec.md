# audit-logging Specification

## Purpose
TBD - created by archiving change optimize-audit-logs. Update Purpose after archive.
## Requirements
### Requirement: Show formatted JSON in log details
The system MUST format JSON fields (Request Params, Response Body) in the log detail view for better readability.

#### Scenario: Viewing a log with JSON body
Given I am viewing the audit log list
When I click on "Detail" for a log entry with JSON request params
Then I should see the request parameters formatted for readability

### Requirement: Asynchronous Logging
系统**必须 (MUST)** 采用非阻塞方式记录审计日志，以确保日志写入操作不影响主业务接口的响应时间。

#### Scenario: Background Task Execution
- **GIVEN** 一个进入系统的 API 请求
- **WHEN** 业务逻辑处理完成并准备返回响应时
- **THEN** 系统应启动一个后台任务（如 FastAPI BackgroundTasks）异步执行数据库写入操作
- **AND** 接口应立即返回响应，无需等待日志写入完成。

