# Tasks: Add SSO Login Integration

## 1. 配置管理
- [ ] 在 `app/core/config.py` 中添加 SSO 配置项
  - [ ] SSO_API_URL: Yovole SSO API 地址
  - [ ] SSO_ACCESS_TOKEN: SSO 访问令牌
  - [ ] SSO_REQUEST_SYSTEM: 请求系统标识
  - [ ] SSO_REQUEST_BUSINESS: 请求业务标识
  - [ ] SSO_TIMEOUT: API 超时时间（默认 30 秒）
- [ ] 在 `env.example` 中添加 SSO 配置示例
- [ ] 更新 `.env` 文件（开发环境）

## 2. 后端实现
- [ ] 在 `app/services/auth_service.py` 中添加 SSO 认证方法
  - [ ] 实现 `authenticate_sso_user(username, password)` 方法
  - [ ] 调用 Yovole SSO API 进行认证
  - [ ] 处理 SSO API 响应和错误
  - [ ] SSO 验证成功后查询本地用户信息
  - [ ] 验证用户状态（status=1）
- [ ] 在 `app/api/portal/endpoints/auth.py` 中添加 SSO 登录接口
  - [ ] 创建 `SSOLoginRequest` 模型
  - [ ] 实现 `POST /api/portal/auth/sso/login` 接口
  - [ ] 处理 SSO 登录成功和失败场景
  - [ ] 返回用户信息和 API Key

## 3. 前端实现
- [ ] 修改 `frontend/src/views/Login.vue`
  - [ ] 移除 SSO 标签页的"暂未开放"提示
  - [ ] 实现 SSO 登录表单（用户名 + 密码输入框）
  - [ ] 调用 `/api/portal/auth/sso/login` 接口
  - [ ] 处理 SSO 登录响应和错误提示
  - [ ] 登录成功后跳转到 Dashboard

## 4. 数据库支持
- [ ] 验证 `api_users` 表结构
  - [ ] 确认用户表包含必要字段（user_name, role, status, api_key_hash）
  - [ ] 确认用户可以通过 user_name 查询
- [ ] 无需修改数据库结构

## 5. 测试
- [ ] 编写 SSO 认证单元测试
  - [ ] 测试 SSO API 调用成功场景
  - [ ] 测试 SSO API 调用失败场景
  - [ ] 测试用户不存在场景
  - [ ] 测试用户被禁用场景
- [ ] 编写 SSO 登录接口集成测试
  - [ ] 测试 SSO 登录成功
  - [ ] 测试 SSO 登录失败（无效凭证）
  - [ ] 测试 SSO 登录失败（用户不存在）
  - [ ] 测试 SSO 登录失败（用户被禁用）
  - [ ] 测试 SSO 登录失败（API 超时）
- [ ] 前端手动测试
  - [ ] 测试 SSO 登录表单显示
  - [ ] 测试 SSO 登录成功流程
  - [ ] 测试 SSO 登录失败提示

## 6. 文档更新
- [ ] 更新 `README.md` 添加 SSO 登录说明
- [ ] 更新 `docs/API_INTEGRATION_GUIDE.md` 添加 SSO 认证文档
- [ ] 更新 `tests/CHECKLIST.md` 添加 SSO 测试状态

## 7. 部署准备
- [ ] 更新 Docker 配置（如果需要）
- [ ] 准备生产环境 SSO 配置
- [ ] 验证生产环境 SSO API 连通性
