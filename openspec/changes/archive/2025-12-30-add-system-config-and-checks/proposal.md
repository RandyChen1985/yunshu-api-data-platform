# Add System Config & Checks

## Summary
本提案旨在增强系统运维能力，新增“系统配置”管理模块，支持管理员在运行时对核心组件（ClickHouse, Redis）进行连接测试与诊断。同时优化系统启动流程，增加 MySQL 连接自检，并兼容旧版本 ClickHouse 的认证方式。

## Motivation
- **运维诊断**: 当前系统连接失败时缺乏直观的诊断工具，管理员无法快速判断是网络问题还是配置问题。
- **启动自检**: 系统启动时虽建立了连接池，但未显式验证连接可用性，可能导致服务启动后首个请求报错。
- **兼容性**: 生产环境存在旧版 ClickHouse 使用无密码/默认用户的情况，当前配置强校验导致无法连接。

## Proposed Changes
1.  **后端 API**:
    - 新增 `/api/portal/system` 路由模块。
    - 实现 `test-connection` 接口，支持 ClickHouse 和 Redis 的连通性测试，返回详细执行日志。
    - 增强 MySQL `init_db` 逻辑，在启动时执行 `SELECT 1` 心跳检测。
2.  **配置适配**:
    - 修改 `app/core/config.py`，允许 `CLICKHOUSE_PASSWORD` 为空或 None。
    - 调整 ClickHouse 连接初始化逻辑，正确处理空密码认证。
3.  **前端 Portal**:
    - 新增“系统配置”菜单（仅 Admin 可见）。
    - 开发系统配置页面，提供连接测试按钮和实时日志展示区。

## Alternatives Considered
- **仅日志**: 只依赖后台日志排查。缺点：管理员无权访问服务器日志时无法排查。
- **自动检测**: 定时任务自动检测。缺点：无法满足即时诊断需求，且增加系统负载。
