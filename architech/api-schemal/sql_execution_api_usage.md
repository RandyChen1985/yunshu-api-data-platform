# SQL执行API使用指南

## 概述

这是一个用于执行动态SQL查询的API端点，专门用于SELECT查询操作。该API提供了安全的数据库查询功能，具有权限验证、SQL安全检查和自动结果限制功能。

## API端点信息

- **路径**: `/v1/execute`
- **方法**: `POST`
- **功能**: 执行安全的SELECT查询并返回结果
- **认证**: 需要API密钥认证
- **权限**: 需要 `system.sql.execute` 权限

## 请求结构

### 请求体参数

| 参数名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| `data_source` | int 或 string | 是 | 目标数据源的ID或名称 |
| `sql` | string | 是 | 原始SQL查询语句（仅支持SELECT） |
| `params` | object | 否 | 可选的参数绑定对象 |

### SQL安全限制

1. **仅支持SELECT语句**: API只允许执行SELECT查询，不允许任何修改或删除操作
2. **禁止的关键词**: 
   - `DROP`, `DELETE`, `UPDATE`, `INSERT`, `ALTER`, `TRUNCATE`
   - `GRANT`, `REVOKE`, `CREATE`, `RENAME`, `REPLACE`
3. **自动限制结果**: 如果查询没有LIMIT子句，系统会自动添加 `LIMIT 1000`

## 响应结构

### 成功响应 (200)

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "columns": [
      {
        "name": "列名",
        "type": "数据类型"
      }
    ],
    "items": [
      ["行1的值1", "行1的值2", ...],
      ["行2的值1", "行2的值2", ...]
    ]
  }
}
```

### 错误响应

| 状态码 | 原因 |
|--------|------|
| 400 | SQL格式错误或包含禁止的关键词 |
| 403 | 权限不足，缺少 `system.sql.execute` 权限 |
| 404 | 指定的数据源不存在 |

## 使用示例

### 示例1: 基本查询 (使用数据源ID)

```json
{
  "data_source": 1,
  "sql": "SELECT id, name, email FROM users WHERE age > 25",
  "params": null
}
```

### 示例2: 使用数据源名称

```json
{
  "data_source": "my_clickhouse_db",
  "sql": "SELECT * FROM events WHERE created_at > '2023-01-01'",
  "params": null
}
```

### 示例3: 带参数的查询

```json
{
  "data_source": 2,
  "sql": "SELECT * FROM orders WHERE user_id = %s AND status = %s",
  "params": {
    "param1": 123,
    "param2": "active"
  }
}
```

### 示例4: 复杂查询 (WITH语句)

```json
{
  "data_source": "analytics_db",
  "sql": "WITH recent_orders AS (SELECT * FROM orders WHERE created_at > '2023-01-01') SELECT COUNT(*) FROM recent_orders",
  "params": null
}
```

## 安全特性

1. **权限验证**: 
   - 管理员用户可绕过权限检查
   - 普通用户必须拥有 `system.sql.execute` 权限

2. **SQL注入防护**:
   - 自动验证SQL语句安全性
   - 阻止包含破坏性关键词的查询

3. **结果限制**:
   - 默认限制返回1000条记录
   - 防止大量数据查询导致系统过载

4. **审计日志**:
   - 所有查询操作都会记录到审计日志中
   - 记录用户ID、数据源ID、执行时间、状态和错误信息

## 注意事项

1. **数据源ID vs 名称**: 可以使用整数ID或字符串名称来指定数据源
2. **查询性能**: 对于大数据集，建议在SQL中使用LIMIT子句来限制结果数量
3. **参数绑定**: 如果使用参数化查询，确保参数格式正确
4. **错误处理**: 响应中的错误信息会提供具体的失败原因

## 调用流程

1. **认证**: 通过API密钥进行身份验证
2. **权限检查**: 验证用户是否具有 `system.sql.execute` 权限
3. **SQL验证**: 检查SQL是否为安全的SELECT语句
4. **限制强制**: 自动添加LIMIT子句（如果未指定）
5. **数据源获取**: 根据ID或名称获取目标数据源配置
6. **查询执行**: 使用对应的数据适配器执行查询
7. **结果返回**: 返回格式化的查询结果
8. **审计记录**: 记录查询操作到审计日志

## 适用场景

- 数据分析和报表生成
- 动态查询需求
- 临时数据提取
- 管理员数据查看
- 数据验证和测试