# 设计：管理门户架构

## 1. 系统架构
采用前后端分离开发，但在部署时合二为一。前端构建为静态资源 (HTML/JS/CSS)，由 FastAPI 服务直接托管。

```mermaid
graph TD
    User[用户/管理员] -->|HTTPS| FastAPI[Python Server (FastAPI)]
    FastAPI -->|/api/v1/*| ServiceAPI[Public Data Service]
    FastAPI -->|/api/portal/*| PortalAPI[Management API]
    FastAPI -->|/*| Static[StaticFiles (Frontend Dist)]
    ServiceAPI --> DB
    PortalAPI --> DB
```

## 2. 认证流程 (Authentication)
由于用户明确要求 "通过 API Key 登录"，我们采用极简的 Token 认证模式。

1. **Login Page**: 用户输入 API Key。
2. **Verify**: 前端调用 `GET /api/portal/auth/me` (附带 Key Header)。
3. **Session**: 验证成功后，Key 存入 `localStorage`。
4. **ACL**: 后端根据 Key 的关联角色 (`admin` vs `user`) 返回菜单权限。

## 3. 功能模块
### 3.1 审计日志 (Audit Logs)
- 如果是 Admin: 可查询 `SELECT * FROM api_access_logs` (支持按 user_name 筛选)。
- 如果是 User: 仅查询 `WHERE user_name = current_user`。

### 3.2 接口测试 (API Playground)
为了避免重复造轮子，我们将集成成熟的开源方案：
- **方案 A (推荐)**: 集成 [Scalar](https://github.com/scalar/scalar) 或 [Swagger UI] 的 Vue 组件。
    - 优点: 自动解析 OpenAPI (fastapi `/openapi.json`)，零配置，界面现代。
    - 实现: 在前端页面引入 `<ScalarApiReference />`，并配置当前的 `openapi.json` URL。
- **自定义增强**: 在标准 UI 外包裹一层 Key 选择器，自动将当前 Session 的 API Key 注入到请求 Header 中。

## 4. 目录结构
```
/
├── app/
│   ├── api/v1/endpoints/
│   │   ├── admin.py  # [NEW] 管理员接口
│   │   └── user.py   # [NEW] 用户自服务接口
├── frontend/         # [NEW] 前端工程
│   ├── src/
│   ├── package.json
│   └── vite.config.js
```
