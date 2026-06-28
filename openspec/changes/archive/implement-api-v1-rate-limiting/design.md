# Design: API v1 动态流控系统

## 1. 架构概览
流控系统作为 FastAPI 的依赖项（Dependency）集成，在业务逻辑执行前对请求进行拦截。

```text
Request -> API Key Auth -> Rate Limiting Check -> Business Logic
```

## 2. 存储设计
- **配置存储 (MySQL)**: `sys_config` 表。
  - `ratelimit.enabled`: 'true' / 'false'
  - `ratelimit.admin.limit`: 管理员每分钟限制次数
  - `ratelimit.user.limit`: 普通用户每分钟限制次数
- **计数存储 (Redis)**:
  - Key 格式: `rate_limit:{user_id}:{minute_timestamp}`
  - Value: 计数器
  - TTL: 60 秒

## 3. 核心逻辑 (后端)
```python
async def check_rate_limit(request: Request, user: Dict = Depends(require_api_key)):
    # 1. 故障回退: 若 Redis 连接失败，直接返回，不影响业务
    # 2. 查找限流值 (按优先级):
    #    a. user_info['rate_limit'] (api_users 表)
    #    b. role_info['rate_limit'] (sys_roles 表)
    #    c. sys_config['ratelimit.{role}.limit'] (全局默认)
    # 3. Redis 计数与 TTL 设置
    # 4. 计算并注入响应头:
    #    X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset
```

## 4. 数据库变更
- `api_users`: 增加 `rate_limit` (INT, 默认为 NULL)
- `sys_roles`: 增加 `rate_limit` (INT, 默认为 NULL)

## 5. 缓存一致性与实时性
为了确保修改配置后立即生效，采用“更新触发失效”策略：
- **操作触发**：当管理员通过 UI 修改全局、角色或用户限流值时。
- **动作**：后端在 `commit` 数据库事务后，立即调用 `redis.delete()` 删除对应的配置缓存键。
- **生效周期**：下一次 API 请求触发流控检查时，会因缓存缺失（Cache Miss）而强制读取数据库，实现秒级生效。

## 6. 峰值统计设计
- **API**: `GET /api/portal/dashboard/api-peak-24h`
- **逻辑**: 
  - 查询 `api_access_stats_1m` 表（分钟级聚合表）。
  - 按小时分组，计算每小时内 `total_calls` 的最大值 (`MAX`)。
  - 该值代表了该小时内最繁忙的那一分钟的请求压力。
- **展示**: 前端使用柱状图或折线图展示，并在图表上标注当前的限流阈值作为参考线。

## 5. 性能优化 (Caching)
后端 `ConfigService` 将缓存 `sys_config` 中的流控参数，减少数据库查询压力。

## 5. 前端交互
在 `SystemConfig.vue` 中新增 Tab，包含：
- 流控总开关（Toggle）
- 管理员限流值（Number Input）
- 普通用户限流值（Number Input）
- 运维日志记录（修改配置时记录到 `sys_maintenance_log`）
