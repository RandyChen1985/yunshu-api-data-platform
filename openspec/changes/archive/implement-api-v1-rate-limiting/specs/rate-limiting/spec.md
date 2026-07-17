# Spec Delta: API v1 Rate Limiting

## MODIFIED Requirements: api-schema/security

### Requirement: 全局流控检查 (Global Rate Limiting)
系统必须对所有 /api/v1 接口执行基于 Redis 的流控检查。系统应在响应头中返回限流状态信息。

#### Scenario: 响应头告知
- **Given** 用户发起有效请求
- **Then** 响应头必须包含 `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`
- **And** 客户端可根据这些信息调整发送频率

### Requirement: 多级限流值覆盖 (Hierarchical Overrides)
限流阈值应支持按用户、角色和系统全局三个级别进行配置。

#### Scenario: 用户级覆盖
- **Given** 全局限流为 100
- **And** 管理员为用户 A 设置了专用限流 500
- **When** 用户 A 发起请求
- **Then** 系统应允许用户 A 在一分钟内发送 500 个请求

#### Scenario: 故障自动降级
- **Given** Redis 服务不可用
- **When** 用户发起 API 请求
- **Then** 系统应记录警告日志并跳过限流检查正常返回数据（Fail-Open）

### Requirement: 动态参数配置
流控阈值必须支持通过管理后台动态修改，且无需重启服务。

### Requirement: 决策辅助数据支持
系统必须提供历史请求峰值数据，以辅助管理员设定合理的限流阈值。

#### Scenario: 获取 24 小时峰值分布
- **Given** 管理员进入流控配置页面
- **When** 页面请求最近 24 小时峰值数据
- **Then** 系统应返回按小时分组的分钟级最高请求次数
- **And** 数据应排除系统内部调用的干扰（如 user_name = 'ALL' 汇总项，或根据具体业务需求过滤）

## ADDED Requirements: nanzi-schema/system-config

### Requirement: 流控配置项存储
系统必须在 `sys_config` 表中维护以下流控参数。

| 配置键 | 说明 | 默认值 |
| :--- | :--- | :--- |
| `ratelimit.enabled` | 流控总开关 (true/false) | true |
| `ratelimit.admin.limit` | 管理员每分钟限制次数 | 1000 |
| `ratelimit.user.limit` | 普通用户每分钟限制次数 | 100 |
