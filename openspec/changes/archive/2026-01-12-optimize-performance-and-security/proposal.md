# Performance and Security Optimization Proposal

## Summary
本提案旨在解决当前系统存在的关键性能瓶颈和安全隐患。主要包括：
1.  **性能优化**: 审计日志写入异步化、MetaService 元数据缓存迁移至 Redis。
2.  **安全增强**: SQL 执行接口引入 AST 解析进行严格校验、数据源接口对敏感字段（密码）进行脱敏。

## Motivation
### Performance
- **审计日志**: 当前日志写入在 HTTP 请求的主线程中同步执行（await），直接增加了接口的响应延迟，高并发下可能成为瓶颈。
- **元数据缓存**: `MetaService` 使用进程内内存字典缓存，在多 Worker 部署模式下会导致缓存不一致，且无法共享，影响扩展性。

### Security
- **SQL 注入**: `sql_execution` 接口目前的正则过滤不够严谨，容易被复杂的 SQL 构造绕过。
- **敏感信息泄露**: 数据源管理接口直接返回包含加密密码的完整对象，虽然已加密，但暴露给前端仍违背最小权限原则。

## Proposed Changes
1.  **Asynchronous Audit Logging**: 利用 FastAPI `BackgroundTasks` 将日志写入移出请求/响应关键路径。
2.  **Distributed Caching**: 改造 `MetaService`，使用 Redis 替代内存字典作为缓存后端，并设置 TTL。
3.  **Robust SQL Validation**: 引入 `sqlparse` 库，基于 AST 解析验证 SQL 语句是否为纯 `SELECT` 查询。
4.  **Sensitive Data Masking**: 在 `DataSourceResponse` 模型中对 `password` 字段进行掩码处理。
