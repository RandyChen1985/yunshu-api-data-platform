# 通用 SQL 执行接口 (SQL Execution Endpoint)

## 目标 (Goal)
新增一个通用 API 端点 `/api/v1/sql/execute`，允许在受控环境下执行原生 SQL 查询。该接口不仅支持 ChatBI，也适用于其他需要灵活取数的场景（如报表工具、调试工具）。

## 背景 (Context)
原计划为 ChatBI 提供的 SQL 执行能力具有通用性。为了避免重复建设，将其设计为通用的 SQL 执行服务。

## 变更内容 (What Changes)
- **新增 API 端点**: `POST /api/v1/sql/execute`
- **请求参数**:
    - `data_source_id`: 目标数据源 ID。
    - `sql`: 待执行的 SQL。
- **核心逻辑**:
    - **权限控制**: 引入系统资源 `system.sql.execute`，必须显式授权。
    - **安全增强**: 强制只会 `SELECT`，强制 `LIMIT`，拦截 DML/DDL。
    - **执行**: 通过 `DataSourceAdapter` 执行。
    - **审计**: 全量记录审计日志。
