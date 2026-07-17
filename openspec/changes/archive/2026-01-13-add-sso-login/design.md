# Design: SSO Login Integration

## Context
系统需要集成 Yovole 统一认证系统，支持企业 SSO 登录。当前系统已预留数据库字段（sso_source, sso_id, email）和前端 UI，但尚未实现 SSO 认证逻辑。

### Constraints
- 必须与 Yovole SSO API 兼容
- 必须保持与现有 API Key 和密码登录的兼容性
- 必须处理 SSO API 不可用的情况
- 必须确保 SSO 凭证的安全传输

### Stakeholders
- 系统管理员：需要配置 SSO 参数
- 最终用户：需要通过 SSO 登录
- 开发团队：需要维护 SSO 集成代码

## Goals / Non-Goals

### Goals
- 实现 Yovole SSO 认证集成
- 支持 SSO 验证成功后查询本地用户
- 提供良好的用户体验和错误提示
- 确保 SSO 认证的安全性

### Non-Goals
- 不支持其他 SSO 提供商（如 OAuth2、SAML）
- 不实现 SSO 用户自动创建
- 不实现 SSO 用户信息同步

## Decisions

### Decision 1: SSO 认证流程
**选择**: 使用 Yovole SSO API 进行用户名密码验证

**理由**:
- Demo.md 提供了现成的 API 调用示例
- Yovole SSO API 已在企业内部广泛使用
- 实现简单，无需复杂的 OAuth2 流程

**实现**:
```
用户输入用户名密码 
→ 调用 Yovole SSO API 
→ 验证成功后查询本地用户 
→ 验证用户状态 
→ 返回用户信息和 API Key
```

### Decision 2: SSO 用户查询策略
**选择**: SSO 验证成功后查询本地用户信息

**理由**:
- 用户必须先在数据库中存在才能通过 SSO 登录
- 保持用户管理的可控性
- 避免自动创建用户带来的安全风险

**实现**:
- SSO 验证成功后，通过用户名查询本地用户
- 验证用户状态（status=1）
- 返回用户信息和 API Key
- 如果用户不存在或被禁用，返回错误

### Decision 4: SSO API 调用方式
**选择**: 使用 httpx 异步 HTTP 客户端

**理由**:
- 项目已使用 httpx 作为 HTTP 客户端
- 支持异步调用，不阻塞主线程
- 支持超时控制和重试机制

**实现**:
```python
async with httpx.AsyncClient(timeout=SSO_TIMEOUT) as client:
    response = await client.post(
        SSO_API_URL,
        headers=headers,
        json=payload,
        verify=False  # 开发环境禁用 SSL 验证
    )
```

### Decision 5: SSO 配置管理
**选择**: 使用环境变量配置 SSO 参数

**理由**:
- 符合项目现有的配置管理方式
- 便于不同环境（开发/测试/生产）的配置
- 避免敏感信息硬编码

**实现**:
```python
SSO_API_URL: str = Field(default="https://yovole.net/api/v1/user/check/login")
SSO_ACCESS_TOKEN: str = Field(default="laplace")
SSO_REQUEST_SYSTEM: str = Field(default="NANZI_API_DATA_PLATFORM")
SSO_REQUEST_BUSINESS: str = Field(default="USER-LOGIN")
SSO_TIMEOUT: int = Field(default=30)
```

## Risks / Trade-offs

### Risk 1: SSO API 不可用
**影响**: 用户无法通过 SSO 登录
**缓解措施**:
- 提供清晰的错误提示
- 建议用户使用其他登录方式（API Key 或密码）
- 监控 SSO API 可用性

### Risk 2: SSO API 响应慢
**影响**: 登录响应时间增加
**缓解措施**:
- 设置合理的超时时间（30 秒）
- 使用异步调用避免阻塞
- 考虑添加 SSO API 响应缓存

### Risk 3: 用户不存在
**影响**: 用户无法通过 SSO 登录
**缓解措施**:
- 提供清晰的错误提示
- 建议用户联系管理员创建账户

### Risk 4: 安全性
**影响**: SSO 凭证泄露或被劫持
**缓解措施**:
- 使用 HTTPS 传输（生产环境）
- Access Token 存储在环境变量中
- 不在日志中记录 SSO 凭证
- 限制 SSO API 调用频率

## Migration Plan

### Phase 1: 配置和后端实现
1. 添加 SSO 配置到 `app/core/config.py`
2. 实现 `AuthService.authenticate_sso_user()` 方法
3. 添加 SSO 登录接口 `/api/portal/auth/sso/login`
4. 编写单元测试

### Phase 2: 前端实现
1. 修改 `Login.vue` 启用 SSO 登录
2. 实现 SSO 登录表单
3. 处理 SSO 登录响应和错误
4. 前端手动测试

### Phase 3: 测试和文档
1. 编写集成测试
2. 更新文档
3. 准备生产环境配置

### Rollback Plan
- 如果 SSO 登录出现问题，可以禁用 SSO 标签页
- 保留 API Key 和密码登录作为备用方案
- 可以通过配置禁用 SSO 功能

## Open Questions

1. **SSO 用户角色**: SSO 用户的默认角色是什么？
   - 建议: 默认为 "user"，管理员手动提升权限

2. **SSO 用户邮箱**: SSO API 是否返回用户邮箱？
   - 建议: 如果返回则存储，否则使用用户名作为邮箱

3. **SSO API SSL 验证**: 生产环境是否需要启用 SSL 验证？
   - 建议: 生产环境启用，开发环境禁用

4. **SSO 用户信息更新**: 是否需要定期同步 SSO 用户信息？
   - 建议: 暂不实现，仅在首次登录时获取

## Implementation Notes

### SSO API 请求格式
```json
{
  "requestSystem": "NANZI_API_DATA_PLATFORM",
  "requestBusiness": "USER-LOGIN",
  "operationType": "LOGIN",
  "userName": "username",
  "password": "password"
}
```

### SSO API 响应格式
```json
{
  "data": true/false
}
```

### SSO 用户查询逻辑
```python
# 1. SSO 验证成功后，查询本地用户
SELECT * FROM api_users WHERE user_name = 'username' AND status = 1

# 2. 如果用户不存在，返回错误
raise HTTPException(status_code=401, detail="User not found")

# 3. 如果用户被禁用，返回错误
raise HTTPException(status_code=401, detail="User is disabled")

# 4. 返回用户信息和 API Key
return user_info
```

### 错误处理
- SSO API 超时: 返回 503 Service Unavailable
- SSO API 错误: 返回 401 Unauthorized
- SSO API 返回 false: 返回 401 Unauthorized
- 用户不存在: 返回 401 Unauthorized
- 用户被禁用: 返回 401 Unauthorized
- 数据库错误: 返回 500 Internal Server Error
