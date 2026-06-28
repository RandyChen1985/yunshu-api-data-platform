# Tasks: Performance and Security Optimization

## 1. 性能优化 (Performance)

### 1.1 审计日志异步化 <!-- id: 0 -->
- [ ] 封装日志写入函数为独立的辅助函数 <!-- id: 1 -->
- [ ] 在 `AccessLogMiddleware` 中使用 `asyncio.create_task` 或其他非阻塞方式调用写入逻辑 <!-- id: 2 -->
- [ ] 在 `sql_execution.py` 中使用 `BackgroundTasks` 替换同步 `await _insert_audit_log` <!-- id: 3 -->
- [ ] 验证：发起请求并观察接口响应耗时是否有明显下降，同时确认日志在后台写入成功 <!-- id: 4 -->

### 1.2 分布式缓存迁移 <!-- id: 5 -->
- [ ] 在 `MetaService` 中引入 `app.core.redis` 模块 <!-- id: 6 -->
- [ ] 重构 `get_config` 方法：先从 Redis 读取，缺失则从 DB 加载并存入 Redis <!-- id: 7 -->
- [ ] 在元数据更新/删除的 Service 方法中添加缓存失效逻辑 <!-- id: 8 -->
- [ ] 验证：手动修改 DB 数据但不触发 Service 更新，确认接口仍返回旧缓存；触发更新后确认缓存已刷新 <!-- id: 9 -->

## 2. 安全增强 (Security)

### 2.1 SQL AST 校验升级 <!-- id: 10 -->
- [ ] 在 `requirements.txt` 中添加 `sqlparse` <!-- id: 11 -->
- [ ] 在 `sql_execution.py` 中引入 `sqlparse` 替换正则校验逻辑 <!-- id: 12 -->
- [ ] 编写测试用例覆盖复杂的 SQL 绕过场景（如注释、多语句、子查询等） <!-- id: 13 -->
- [ ] 验证：确保合法的 `SELECT` 正常通过，破坏性语句被准确拦截 <!-- id: 14 -->

### 2.2 敏感信息脱敏 <!-- id: 15 -->
- [ ] 修改 `app/schemas/datasource.py` 中的 `DataSourceResponse` 模型 <!-- id: 16 -->
- [ ] 使用 Pydantic 的 `@field_validator` 或 `computed_field` 将 `password` 默认设为 `******` <!-- id: 17 -->
- [ ] 检查并确保管理后台的“测试连接”和“更新”逻辑不受脱敏影响（通常编辑时密码为空代表不修改） <!-- id: 18 -->
- [ ] 验证：通过 Swagger UI 查看数据源接口返回结果 <!-- id: 19 -->

## 3. 回归测试 <!-- id: 20 -->
- [ ] 执行全量自动化测试 `tests/run_tests.sh` <!-- id: 21 -->
- [ ] 更新 `tests/CHECKLIST.md` <!-- id: 22 -->
