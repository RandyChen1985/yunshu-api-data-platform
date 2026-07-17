# Design: Performance and Security Optimization

## Architecture Overview

### 1. Async Logging Strategy
我们将使用 FastAPI 提供的 `BackgroundTasks`。
- **优点**: 简单易用，不需要引入额外的消息队列（如 Celery/RabbitMQ），适合当前的 QPS 规模。
- **流程**:
    1.  `AccessLogMiddleware` 捕获数据。
    2.  不再在中间件中 `asyncio.create_task`（可能导致某些环境下的资源泄露或无法注入 BackgroundTasks）。
    3.  建议在 Endpoint 层面注入 `BackgroundTasks`，或者在 Middleware 中安全地启动异步非阻塞任务。
    *注：由于 AccessLogMiddleware 是 BaseHTTPMiddleware，直接使用 BackgroundTasks 比较困难。我们将继续使用 `asyncio.create_task` 但进行稳健封装，或者调整中间件实现方式。*

### 2. Distributed Metadata Caching
- **Backend**: Redis。
- **Key 策略**: `nanzi:meta:config:{resource_key}`。
- **过期时间 (TTL)**: 默认 3600 秒 (1小时)。
- **同步机制**: 当元数据更新时（通过管理后台），主动失效（Delete）对应的 Redis Key。

### 3. SQL Parser Integration
- **库选择**: `sqlparse`。
- **逻辑**:
    ```python
    import sqlparse
    parsed = sqlparse.parse(sql)
    for statement in parsed:
        if statement.get_type() != "SELECT":
            raise HTTPException(...)
    ```
- **防护深度**: AST 解析比正则更能识别嵌套查询、注释混淆等注入手段。

### 4. Response Masking
- **Pydantic Validator**:
    在 `DataSourceResponse` 中对 `password` 字段增加一个 `@field_validator` 或直接在返回前手动处理。
    由于前端可能需要编辑功能，密码通常不应通过查询接口返回。前端编辑时应单独提供“重置密码”功能。

## Trade-offs
- **Redis 依赖**: 增加了系统对 Redis 的强依赖。如果 Redis 挂了，MetaService 需要有降级回库查询的逻辑。
- **性能开销**: `sqlparse` 解析 AST 相比正则略有性能损耗，但在当前应用场景下可忽略不计。
