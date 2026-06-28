# 设计方案: 通用 SQL 执行 (Design: General SQL Execution)

## 架构设计 (Architecture)
新增 `app/api/v1/endpoints/sql_execution.py`。

## 安全模型 (Security Model)
1.  **强制只读**: 仅允许 `SELECT`。
2.  **关键字拦截**: 拦截 `DROP`, `DELETE`, `UPDATE` 等。
3.  **认证鉴权**:
    -   认证: API Key。
    -   授权: 检查用户是否拥有 `system.sql.execute` 资源权限。
4.  **行数限制**: 强制追加或截断至 `LIMIT 1000`。
5.  **审计日志**: 记录 `user_id`, `sql`, `status`, `duration` 到 `sys_api_audit_log`。

## 适配器扩展 (Adapter Extension)
现有的 `DataSourceAdapter.execute(query: LogicalQuery)` 是为结构化逻辑查询设计的。
我们需要在 `DataSourceAdapter` 基类中新增 `execute_sql(self, sql: str, params: Dict[str, Any] = None)` 抽象方法，并在支持的适配器（ClickHouse, MySQL）中实现它，以支持原生 SQL 执行。查询
## 接口设计 (API Design)
- **Router Tag**: `["通用查询"]`
- **Method/Path**: `POST /api/v1/sql/execute` (注意: 这是一个独立的 Router，但在 Swagger UI 中与 query 归为同一组)
- **Summary**: `动态 SQL 查询`
- **Description**: 
    > 执行动态 SQL 查询。
    >
    > **使用说明**:
    > 1.  **数据源**: 通过 `data_source_id` 指定目标数据库。
    > 2.  **安全性**: 仅支持 `SELECT` 语句。所有查询会自动追加 `LIMIT 1000` 防止过载。
    > 3.  **权限**: 必须拥有 `system.sql.execute` 资源权限。
- **Request Body**: 
    ```json
    { 
      "data_source_id": 1, 
      "sql": "SELECT * FROM my_table WHERE region = %(region)s",
      "params": { "region": "East" }  // 可选，用于参数化查询
    }
    ```
- **Response**: `{ "code": 200, "data": { "columns": [...], "items": [...] } }`
