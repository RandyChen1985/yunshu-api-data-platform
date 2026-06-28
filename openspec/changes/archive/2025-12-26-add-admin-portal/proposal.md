# 提案：管理与开发者门户 (Admin & Developer Portal)

## Why
- **自助服务 (Self-Service)**:目前 API Key 分发和重置依赖人工操作 (SQL/Script)，效率低下。
- **可观测性 (Observability)**: 用户无法查看自己的调用记录和配额使用情况。
- **开发体验 (DX)**: 缺乏交互式的 API 调试工具，开发者接入成本高。

## What Changes
- **前端 (Frontend)**: 新增 `frontend/` 目录，构建基于 Vue 3 + TailwindCSS 的单页应用 (SPA)。
    - **部署模式**: 编译产物 (`dist/`) 直接由 FastAPI 的 `StaticFiles` 挂载服务，无需 Nginx。
    - **角色**: 管理员 (Admin) & 普通用户 (User)。
    - **登录**: 基于 API Key 的无状态认证。
- **后端 (Backend)**:
    - 新增 `/api/portal` 路由组 (专属管理接口，与 `/api/v1` 业务接口隔离)。
    - 包含 `/api/portal/auth` (登录验证), `/api/portal/audit` (审计), `/api/portal/playground` (测试)。
    - 增强 CORS 配置以支持前端调用。

## Risks
- **安全性**: API Key 直接作为登录凭证存储在浏览器中 (虽然是无状态，但存在 XSS 窃取风险)。*缓解措施: 仅允许通过 Key 访问数据接口，敏感操作(如删库)需二次验证(暂不涉及).*
- **工作量**: 引入前端构建流程 (Node.js/Vite)，增加项目复杂度。
