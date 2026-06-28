# Change: Add SSO Login Integration

## Why
当前系统已预留 SSO 数据库字段和前端 UI，但尚未实现 SSO 认证逻辑。为了支持企业统一认证，需要集成 Yovole 统一认证系统，使用户能够通过企业 SSO 一键登录，提升用户体验并简化用户管理。

## What Changes
- **后端实现**：
  - 在 `AuthService` 中添加 SSO 认证方法
  - 创建 SSO 登录接口 `/api/portal/auth/sso/login`
  - 实现 Yovole SSO API 调用逻辑
  - SSO 验证成功后查询本地用户信息
- **前端实现**：
  - 启用 SSO 登录标签页
  - 实现 SSO 登录表单（用户名 + 密码）
  - 处理 SSO 登录响应和错误
- **配置管理**：
  - 添加 SSO 相关配置（API URL、Access Token）
  - 支持环境变量配置
- **数据库**：
  - 无需修改数据库结构
  - 用户必须先在数据库中存在才能通过 SSO 登录

## Impact
- **Affected specs**: `specs/auth/spec.md`
- **Affected code**:
  - `app/services/auth_service.py` - 添加 SSO 认证逻辑
  - `app/api/portal/endpoints/auth.py` - 添加 SSO 登录接口
  - `app/core/config.py` - 添加 SSO 配置
  - `frontend/src/views/Login.vue` - 启用 SSO 登录功能
- **Breaking changes**: 无
- **Security considerations**: 
  - SSO API 调用需要 HTTPS
  - Access Token 需要安全存储
  - 需要处理 SSO API 超时和失败
