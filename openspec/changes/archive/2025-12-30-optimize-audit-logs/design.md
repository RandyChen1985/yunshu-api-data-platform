# 设计文档 (Design Document)

## 搜索逻辑优化

### 现状
当前 SQL 查询构建方式：
```python
if target_user:
    query_conditions.append("user_name = %s")
```
这导致必须输入完整用户名才能匹配。

### 方案
将 `user_name` 和 `client_ip` 的查询改为 `LIKE` 模糊匹配：
```python
if target_user:
    query_conditions.append("user_name LIKE %s")
    params.append(f"%{target_user}%")

if client_ip:
    query_conditions.append("client_ip LIKE %s")
    params.append(f"%{client_ip}%")
```

### 性能考量
虽然 `LIKE %...%` 会导致无法利用索引（如果列上有索引），但考虑到：
1. `api_access_logs` 表通常按时间排序和分页。
2. 审计日志的查询频率相对较低，且通常带有时间范围过滤。
3. MySQL 8.0+ 在特定条件下有一定的优化。
4. 如果数据量极大（千万级），建议后续引入 Elasticsearch 或 ClickHouse 进行日志存储和检索。当前阶段 MySQL `LIKE` 足以满足需求。

## 兼容性
- 此修改仅影响 API 的查询行为，不改变 API 接口定义（参数名不变）。
- 前端无需修改 API 调用逻辑。
