# Design: MySQL 审计日志按日物理分表设计

## 1. 核心模型

### 1.1 模板表 `api_access_logs_template`
用于 `CREATE TABLE ... LIKE` 操作，保持索引一致。
- 包含 `id`, `trace_id`, `user_id`, `user_name`, `endpoint`, `method`, `status_code`, `process_time_ms`, `client_ip`, `request_params`, `response_body`, `action_type`, `source_sql`, `created_at` 等全量字段。

## 2. 写入流程 (Write Flow)

### 2.1 动态路由逻辑
1. 获取当前日期字符串（如 `20260130`）。
2. 构造表名 `table_name = f"api_access_logs_{suffix}"`。
3. **Cache 检查**：维护一个单例 `set` 记录已确认创建的表名。
4. **延迟创建**：若 Cache 缺失，执行 `CREATE TABLE IF NOT EXISTS {table_name} LIKE api_access_logs_template`。
5. **插入数据**：执行 `INSERT INTO {table_name} ...`。

## 3. 查询流程 (Read Flow)

### 3.1 动态 SQL 构建器
为了支持跨天查询，后端提供 `AuditTableRouter`：
```python
def get_tables_in_range(start_date, end_date):
    # 根据范围生成表名列表
    # 检查数据库中实际存在的表
    # 返回 [table1, table2, ...]
```
构建 SQL：`SELECT * FROM (SELECT ... FROM table1 UNION ALL SELECT ... FROM table2) AS combined`。

## 4. 影响范围与兼容性

### 4.1 存量数据
旧的 `api_access_logs` 保持不动。查询逻辑应包含逻辑：如果查询时间早于“分表切换日期”，则路由到旧大表。

### 4.2 字段变更
由于 `action_type` 和 `source_sql` 已经合并到分表中，原有的 `JOIN api_access_logs_ext` 代码块需要移除，直接从主表字段读取。
