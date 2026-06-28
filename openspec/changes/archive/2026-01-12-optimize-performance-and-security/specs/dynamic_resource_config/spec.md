# dynamic_resource_config Specification Delta

## MODIFIED Requirements

### Requirement: 配置缓存 (Configuration Caching)
系统**必须 (MUST)** 实现基于分布式缓存（如 Redis）的元数据管理机制，以确保在多实例部署环境下的数据一致性与读取性能。

#### Scenario: 首次读取写入 Redis (Lazy Loading)
- **Given** 系统刚启动，Redis 缓存为空
- **When** 收到第一个针对 "yunshu_rooms" 的查询请求
- **Then** 系统从 MySQL 查询该配置
- **And** 将配置以 JSON 序列化形式存入 Redis 缓存（设置合理的 TTL）
- **And** 后续相同请求直接从 Redis 读取。

#### Scenario: 修改配置同步更新 (Write-Invalidate)
- **Given** 配置已缓存在 Redis 中
- **When** 管理员通过后台 API 修改或删除了该资源配置
- **Then** 系统应立即删除 Redis 中对应的缓存 Key
- **And** 确保后续请求能触发重新加载。
