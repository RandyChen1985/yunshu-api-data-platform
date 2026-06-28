# Change: Improve Developer Experience

## Why
目前 API 文档虽然基本完备，但在以下方面存在不足：
1. Swagger UI 在刷新后需要重新输入 API Key，调试体验不佳。
2. 缺乏面向外部开发者（尤其是 AI Agent）的快速入门指南和代码示例。
3. 部分复杂 Schema（如通用查询的 filters）描述不够结构化。

## What Changes
- **MODIFIED**: `app/main.py` 优化 Swagger UI 配置，增加 `persistAuthorization: true`。
- **MODIFIED**: `app/api/v1/endpoints/query.py` 增强 Schema 定义和示例。
- **ADDED**: `docs/guides/getting-started.md` 新增开发者快速入门指南。
- **ADDED**: `scripts/examples/api_client_example.py` 提供 Python 接入示例代码。

## Impact
- 影响组件：API 文档服务、通用查询接口。
- 不涉及逻辑变更，不会对现有业务造成破坏性影响。
