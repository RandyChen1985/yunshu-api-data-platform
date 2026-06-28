# 系统安全加固技术规格书 (Security Hardening Spec)

## 1. 概述
本变更旨在全面提升系统的安全性，重点解决 SQL 注入风险、接口越权访问风险及敏感文档泄露问题。

## 2. 核心变更

### 2.1 ClickHouse 适配器安全重构
- **防注入机制**: 移除了不安全的字符串拼接，实现了 `_escape` 方法，对单引号 (`'`) 和反斜杠 (`\`) 进行严格转义。
- **入参校验**: 在构建 SQL 前，对 `metric_time` 和 `event_time` 字段进行强制格式校验：
    - ISO 格式字符串必须符合 `YYYY-MM-DD HH:MM:SS`。
    - 时间戳格式必须为纯数字。
    - 校验失败直接抛出 `ValueError` (HTTP 400/500)。
- **类型兼容**: 针对 ClickHouse `String` 类型存储时间戳的特性，强制将时间字段转换为带引号的字符串值（如 `'1735660800'`），确保比较操作的正确性。

### 2.2 接口鉴权体系升级
- **分级保护**: 在 `app/api/portal/api.py` 中将路由分为两类：
    - **Admin Only**: `/management`, `/keys` (需 Admin 角色)。
    - **Authenticated**: `/audit`, `/dashboard` (需登录，普通用户可访问)。
- **Login/Logout**:
    - 登录成功后下发 `HttpOnly` Cookie (`admin_token`)。
    - 新增 `POST /logout` 接口，显式清除服务端 Cookie。

### 2.3 文档接口保护
- **禁用默认文档**: 禁用了 FastAPI 默认的 `/docs` 和 `/redoc` 路由。
- **自定义鉴权路由**:
    - 重写 `/docs` 和 `/redoc`，增加 `get_current_admin_from_cookie` 依赖。
    - 未携带有效 Cookie 的请求将被重定向至 `/login` 页面。

### 2.4 前端集成
- **退出逻辑**: 更新 `Dashboard.vue`，在用户点击退出时，异步调用后端 `/logout` 接口，确保会话彻底终结。

## 3. 验证结果
- **自动化测试**: 所有 API 测试用例 (65个) 全部通过。
- **手动测试**: 验证了 SQL 注入攻击无效，验证了未登录无法访问文档。
