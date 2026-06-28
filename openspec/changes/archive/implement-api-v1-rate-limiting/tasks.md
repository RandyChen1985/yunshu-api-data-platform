# Tasks: 实现 API v1 动态流控

## 阶段 1: 基础设施与数据准备
- [x] 编写数据库脚本，向 `sys_config` 插入默认流控配置项。 `v=0.1.0`
- [x] 执行 DDL 语句为 `api_users` 和 `sys_roles` 增加 `rate_limit` 字段。 `v=0.1.0`
- [x] 在 `app/services/system_service.py` 中增加统一的配置读取服务（带 Redis 缓存与失效机制）。 `v=0.1.0`

## 阶段 2: 后端逻辑实现
- [x] 在 `app/api/portal/endpoints/dashboard.py` 中新增 `/api-peak-24h` 接口。 `v=0.2.0`
- [x] 更新 `AuthService` 以便在登录/校验时获取用户和角色的 `rate_limit` 属性。 `v=0.2.0`
- [x] 重构 `app/core/dependencies.py` 中的 `check_rate_limit` 函数，支持多级限流值查找、Fail-Open 及 Header 注入。 `v=0.2.0`
- [x] 挂载流控到 API v1 各端点。 `v=0.2.0`
- [x] 实现全链路缓存失效逻辑（更新配置时自动清理相关 Redis Key）。 `v=0.2.1`

## 阶段 3: 前端界面开发
- [x] 在 `SystemConfig.vue` 中新增 `ratelimit` 标签页，包含全局开关和默认值设置。 `v=0.3.0`
- [x] 开发“24 小时请求峰值”监控卡片 (ECharts)。 `v=0.3.0`
- [x] 在 `Users.vue` (用户管理) 的编辑弹窗中增加“限流值”输入项。 `v=0.3.0`
- [x] 在 `Roles.vue` (角色管理) 的编辑界面中增加“限流值”输入项。 `v=0.3.0`

## 阶段 4: 验证与测试
- [x] 编写自动化测试脚本 `tests/api/v1/test_rate_limit.py`，验证不同角色在超限时的响应。 `v=0.4.0`
- [x] 验证 UI 修改参数后，后端流控立即生效（已修复缓存同步问题）。 `v=0.4.0`
- [x] 更新 `tests/CHECKLIST.md`。 `v=0.4.0`
- [x] 修复 MySQL 字符集冲突和 Redis NoneType 写入异常。 `v=0.4.1`