# Redis 缓存与 Key 设计规范

本系统利用 Redis 作为高性能缓存和并发控制层，主要涵盖身份认证、统计分析、动态限流以及业务查询结果缓存四大场景。

## 1. 缓存设计概览

| 类别 | 核心策略 | 典型 TTL | 一致性保障 |
| :--- | :--- | :--- | :--- |
| **认证与权限** | Read-Through | 1 小时 | 更新用户/角色时主动失效 (Invalidate) |
| **Dashboard 统计** | TTL-Based | 1-5 分钟 | 依靠短过期时间自然刷新 |
| **动态流控** | Atomic Counter | 60 秒 | 基于分钟时间戳自动分片，到期自动清理 |
| **系统配置** | Read-Through | 1 小时 | 修改配置时同步清理对应 Key |
| **业务数据** | TTL-Based | 动态 (30s+) | 由资源元数据配置项动态控制 |

---

## 2. Key 规范与细节

### 2.1 身份认证与权限 (Security)
用于减少对 MySQL `api_users` 和 `sys_roles` 表的频繁访问。

| Key 规范 | 说明 | 内容结构 | TTL |
| :--- | :--- | :--- | :--- |
| `auth:api_key:{hashed_key}` | API Key 校验缓存 | 用户 ID, 姓名, 角色, 限流值 | 1h |
| `sys:auth:permissions:v2:user:{uid}` | 聚合权限集缓存 | Menus, Elements, Resources | 1h |

### 2.2 统计分析 (Analytics)
用于加速管理后台首页 (Dashboard) 的响应速度。

| Key 规范 | 说明 | 内容结构 | TTL |
| :--- | :--- | :--- | :--- |
| `dashboard:stats:{role}:{period}` | 总调用量/成功率等卡片 | JSON (Object) | 5m |
| `dashboard:trends24h:{role}` | 24 小时趋势折线图 | JSON (Array) | 5m |
| `dashboard:peak24h:admin` | 24 小时分时分钟峰值 | JSON (Array) | 5m |
| `dashboard:resource-stats:{role}:{period}` | 接口热度排行 | JSON (Array) | 2m |
| `dashboard:user-ranking:{period}` | 用户活跃排行 | JSON (Array) | 2m |
| `dashboard:activities:{role}:{limit}` | 最近活动日志 | JSON (Array) | 1m |

### 2.3 动态流控 (Rate Limiting)
利用 Redis 的 `INCR` 和 `EXPIRE` 实现高性能限流。

| Key 规范 | 说明 | 内容结构 | TTL |
| :--- | :--- | :--- | :--- |
| `ratelimit:v1:{uid}:{YYYYMMDDHHmm}` | API v1 分钟级计数 | Integer (Counter) | 60s |

### 2.4 系统配置 (System Configuration)
存储通过 UI 修改的系统级动态参数。

| Key 规范 | 说明 | 内容结构 | TTL |
| :--- | :--- | :--- | :--- |
| `yunshu:config:{config_key}` | 全局配置项 | String (Value) | 1h |

### 2.5 业务结果缓存 (Business Data)
缓存 ClickHouse 大查询结果，由 `sys_resource_meta.cache_ttl` 控制。

| Key 规范 | 说明 | 内容结构 | TTL |
| :--- | :--- | :--- | :--- |
| `yunshu:query:{res_key}:{params_hash}` | 通用查询接口结果 | JSON (Standard Response) | 动态 |
| `yunshu:sql_exec:{sql_hash}` | SQL 实验室执行结果 | JSON (Standard Response) | 30s |

---

## 3. 运维与开发规范

1.  **主动失效逻辑**：
    *   在 `app/services/permission_service.py` 中封装了 `invalidate_user_cache` 和 `invalidate_role_cache`。
    *   **强制规范**：所有修改用户信息、角色权限、资源授权的代码路径，**必须**调用上述失效方法。
2.  **安全性**：
    *   `auth:api_key` 使用的是 API Key 的 **SHA256 哈希值** 记录，而非明文，确保 Redis 泄露时密钥安全。
3.  **序列化**：
    *   统计类数据存入 Redis 前必须使用 `json.dumps(..., default=str)` 处理，以解决 MySQL `Decimal` 或 `DateTime` 类型的序列化异常。
4.  **监控**：
    *   管理后台“系统设置-连接池监控”可实时查看 Redis 的 Key 数量及分布情况。
