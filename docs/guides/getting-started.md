# 开发者快速入门指南 (Developer Getting Started Guide)

欢迎使用云枢·数据服务平台 API。本指南旨在帮助开发者快速了解如何认证、调用接口以及处理返回结果。

## 1. 认证 (Authentication)

平台使用 **API Key** 进行认证。

- **获取方式**：请联系系统管理员在管理后台生成。
- **使用方式**：所有请求必须在 HTTP Header 中携带 `X-API-Key` 字段。

```http
GET /api/v1/resources/rooms HTTP/1.1
X-API-Key: your_secure_api_key_here
```

## 2. 响应格式 (Response Format)

平台采用统一的 JSON 包装格式：

```json
{
  "code": 200,          // 状态码，200 表示成功
  "message": "success", // 描述信息
  "data": { ... },      // 业务数据
  "timestamp": "...",   // 服务器时间 (ISO8601)
  "trace_id": "..."     // 请求唯一追踪 ID，排障时请提供此 ID
}
```

### 分页响应
对于列表类接口，`data` 结构如下：
- `items`: 当前页数据列表
- `total`: 总条数
- `page`: 当前页码
- `size`: 每页条数
- `pages`: 总页数

## 3. 核心接口：通用逻辑查询 (`/api/v1/query`)

这是平台最强大的接口，允许通过 JSON 定义复杂的查询逻辑，而无需直接编写 SQL。

### 查询参数
- `resource`: 资源名（如 `donghuan_real_metrics`）
- `filters`: 嵌套列表 `[[字段, 操作符, 值], ...]`
- `sort_by`: 排序字段
- `sort_order`: `asc` 或 `desc`

### 支持的操作符
`=`, `!=`, `>`, `<`, `>=`, `<=`, `LIKE` (模糊匹配), `IN` (列表包含)

### 示例请求
查询温度超过 30 度的实时指标：
```json
{
  "resource": "donghuan_real_metrics",
  "filters": [
    ["metric_value", ">", "30"]
  ],
  "sort_by": "metric_time",
  "sort_order": "desc",
  "page": 1,
  "size": 10
}
```

## 4. 常见错误码

- `400`: 请求参数错误（如 resource 不存在，或 filter 格式错误）
- `401`: 认证失败（API Key 缺失或无效）
- `403`: 权限不足（该 API Key 无权访问目标资源）
- `429`: 请求过于频繁（触发限流策略）
- `503`: 服务不可用（通常是底层数据库连接异常）

## 5. 开发者工具

- **交互式文档**: 访问 `/docs` (Swagger UI) 或 `/redoc` (ReDoc)。
- **持久化认证**: Swagger UI 已开启认证持久化，刷新页面无需重复输入 API Key。
