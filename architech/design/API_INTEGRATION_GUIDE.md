# API 集成指南 (Integration Guide)

本文档面向开发者，详细介绍如何集成云枢·数据服务平台 API。通过本指南，您将了解认证机制、核心接口调用逻辑、最佳实践以及常见问题处理。

---

## 1. 快速接入

### 1.1 基本信息

- **Base URL**: `/api/v1`
- **协议**: HTTP/1.1 (推荐使用 HTTPS)
- **数据格式**: JSON

### 1.2 认证机制 (Authentication)

平台采用 **API Key** 进行接口鉴权。您必须在每个 HTTP 请求的 Header 中携带 `X-API-Key`。

**请求示例:**

```http
GET /api/v1/resources/vm_stats HTTP/1.1
Host: your-api-host.example.com
X-API-Key: YOUR_API_KEY_HERE
Content-Type: application/json
```

> [!IMPORTANT]
> API Key 是您的身份凭证，请妥善保管，切勿在客户端代码（如浏览器 JS）中通过硬编码暴露。建议在后端服务器发起调用。

---

## 2. 响应规范

所有 API 返回统一的 JSON 结构，便于客户端解析。

### 成功响应 (200 OK)

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      { "id": 1, "name": "server-01", "cpu_usage": 45.2 },
      { "id": 2, "name": "server-02", "cpu_usage": 12.8 }
    ],
    "total": 100,
    "page": 1,
    "size": 2
  },
  "timestamp": "2024-03-20T10:00:00+08:00",
  "trace_id": "a1b2c3d4-e5f6-7890-a1b2-c3d4e5f67890"  // 请记录此 ID 用于排障
}
```

### 错误响应

非 200 状态码时，response body 依然保持 JSON 格式：

```json
{
  "code": 4011,
  "message": "API Key 缺失",
  "data": null,
  "timestamp": "...",
  "trace_id": "..."
}
```

---

## 3. 核心接口详解

### 3.1 通用逻辑查询 (`POST /query`)

这是平台最核心的接口，支持通过 JSON 配置复杂的筛选逻辑。

**场景**: 
- 需要组合多个筛选条件（AND 关系）。
- 需要模糊匹配、范围查询。

**接口定义**:

```http
POST /api/v1/query
```

**请求体参数**:

| 字段 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `resource` | string | 是 | 资源名称 (需先申请权限) |
| `filters` | array | 否 | 筛选条件列表，格式 `[[字段, 操作符, 值], ...]` |
| `page` | int | 否 | 页码，默认 1 |
| `size` | int | 否 | 每页条数，默认 20，最大 1000 |
| `sort_by` | string | 否 | 排序字段 |
| `sort_order` | string | 否 | `asc` (升序) 或 `desc` (降序) |

**支持的操作符**:

- `=`: 精确匹配
- `!=`: 不等于
- `>`, `>=`, `<`, `<=`: 数值/时间范围比较
- `LIKE`: 字符串模糊匹配 (如 `%demo%`)
- `IN`: 列表包含 (如 `["A", "B"]`)

**完整示例**: 
*查询 `host_metrics` 资源中，CPU 使用率 > 80% 且 状态为 "WARNING" 的最近 10 条记录。*

```json
{
  "resource": "host_metrics",
  "filters": [
    ["cpu_usage", ">", 80],
    ["status", "=", "WARNING"]
  ],
  "sort_by": "created_at",
  "sort_order": "desc",
  "page": 1,
  "size": 10
}
```

### 3.2 资源快捷查询 (`GET /resources/{key}`)

适用于简单的单条件等值查询。

**接口定义**:

```http
GET /api/v1/resources/{resource_key}?param1=value1&param2=value2
```

**示例**:
查询 `users` 资源中 `role=admin` 的用户。

```http
GET /api/v1/resources/users?role=admin&page=1&size=20
```

> [!TIP]
> 如果同一个参数传递多次（如 `?status=active&status=pending`），系统会自动将其转换为 `IN` 查询。

### 3.3 动态 SQL 执行 (`POST /sql/execute`)

**⚠️ 高级接口**: 仅供拥有 `system.sql.execute` 权限的用户（或管理员）使用。

允许直接执行 `SELECT` 语句，适合需要极其复杂查询逻辑（如多表 JOIN、嵌套子查询）的场景。

**接口定义**:

```http
POST /api/v1/sql/execute
```

**请求体参数**:

| 字段 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `data_source` | string/int | 是 | 数据源名称或 ID |
| `sql` | string | 是 | 仅支持 `SELECT` 语句 |
| `params` | object | 否 | 参数化查询绑定的变量（推荐使用，防止注入） |

**安全限制**:
- 仅允许 `SELECT`。
- 强制最大 `LIMIT 1000` (如果未指定)。

**请求示例**:

```json
{
  "data_source": "clickhouse_prod",
  "sql": "SELECT count(*) as total, status FROM host_metrics WHERE time > %(start_time)s GROUP BY status",
  "params": {
    "start_time": "2024-01-01 00:00:00"
  }
}
```

---

## 4. 最佳实践 (Best Practices)

### 4.1 错误处理

建议客户端按照以下逻辑处理错误：

1. **检查 HTTP Status Code**:
    - `2xx`: 业务受理成功，解析 `data`。
    - `4xx`: 客户端参数错误，**不应重试**。请检查 `message` 或 `code` 修正参数。
    - `5xx`: 服务端错误。建议实施 **指数退避重试 (Exponential Backoff)** 策略（如等待 1s, 2s, 4s 后重试）。

2. **关注 `trace_id`**:
    - 每次响应都会包含唯一的 `trace_id`。如果遇到难以解决的问题，请向技术支持提供此 ID，我们能快速定位日志。

### 4.2 性能优化

- **合理使用 `size`**: 尽量避免设置过大的 `size`（如 >500），这会增加数据库 IO 和网络传输耗时。建议分页获取。
- **精确筛选**: 尽可能提供索引字段（如时间、ID）作为筛选条件，避免全表扫描。
- **按需加载**: 如果只需要查看最新数据，务必带上时间字段的倒序排序。

---

## 5. 常见错误码字典

| HTTP 状态 | 业务 Code | 含义 | 处理建议 |
| :--- | :--- | :--- | :--- |
| 400 | 4001 | 无效的参数 | 检查 request body 格式或字段类型 |
| 400 | 4004 | 资源未找到 | 检查 `resource` 名称是否拼写正确 |
| 401 | 4011 | API Key 缺失 | Header 中添加 `X-API-Key` |
| 401 | 4012 | API Key 无效 | 检查 Key 是否过期或被禁用 |
| 403 | 4031 | 访问被拒绝 | 当前 API Key 没有目标资源的权限，请联系管理员申请 |
| 429 | 429 | 请求过于频繁 | 降低请求频率 |
| 500 | 5002 | ClickHouse 错误 | SQL 执行异常，通常是字段不存在或类型不匹配 |
| 503 | 5031 | 数据库连接失败 | 数据库瞬时不可用，建议稍后重试 |
