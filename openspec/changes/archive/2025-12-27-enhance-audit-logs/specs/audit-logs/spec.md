# 技术规格：审计日志增强

## 1. 后端 API 规格

### 1.1 获取日志列表（增强版）

**接口**: `GET /api/portal/audit/logs`

**请求参数**:
```typescript
interface LogQueryParams {
  page?: number;           // 页码，默认 1
  size?: number;           // 每页条数，默认 20，范围 1-100
  start_time?: string;     // 开始时间 (ISO 8601)
  end_time?: string;       // 结束时间 (ISO 8601)
  method?: string;         // HTTP 方法 (GET/POST/PUT/DELETE/PATCH)
  status_code?: number;    // 精确状态码
  min_status?: number;     // 最小状态码 (范围查询)
  max_status?: number;     // 最大状态码 (范围查询)
  endpoint?: string;       // 接口路径 (模糊匹配)
  user_name?: string;      // 用户名 (管理员可用)
  client_ip?: string;      // 客户端 IP
}
```

**响应**:
```typescript
interface LogListResponse {
  total: number;
  page: number;
  size: number;
  items: LogItem[];
  statistics?: Statistics;  // 仅当请求参数包含 include_stats=true
}

interface LogItem {
  id: number;
  trace_id: string;
  user_name: string;
  endpoint: string;
  method: string;
  status_code: number;
  process_time_ms: number;
  client_ip: string;
  created_at: string;
}

interface Statistics {
  total_requests: number;
  success_count: number;      // 2xx
  error_count: number;         // 4xx + 5xx
  success_rate: number;        // 百分比
  avg_response_time: number;   // 毫秒
}
```

**SQL 实现**:
```sql
-- 主查询
SELECT 
  id, trace_id, user_name, endpoint, method, 
  status_code, process_time_ms, client_ip, created_at
FROM api_access_logs
WHERE 
  (start_time IS NULL OR created_at >= :start_time)
  AND (end_time IS NULL OR created_at <= :end_time)
  AND (method IS NULL OR method = :method)
  AND (status_code IS NULL OR status_code = :status_code)
  AND (min_status IS NULL OR status_code >= :min_status)
  AND (max_status IS NULL OR status_code <= :max_status)
  AND (endpoint IS NULL OR endpoint LIKE :endpoint)
  AND (user_name IS NULL OR user_name = :user_name)
  AND (client_ip IS NULL OR client_ip = :client_ip)
ORDER BY created_at DESC
LIMIT :size OFFSET :offset;

-- 统计查询
SELECT 
  COUNT(*) as total_requests,
  SUM(CASE WHEN status_code >= 200 AND status_code < 300 THEN 1 ELSE 0 END) as success_count,
  SUM(CASE WHEN status_code >= 400 THEN 1 ELSE 0 END) as error_count,
  AVG(process_time_ms) as avg_response_time
FROM api_access_logs
WHERE <same conditions>;
```

---

### 1.2 获取日志详情

**接口**: `GET /api/portal/audit/logs/{log_id}`

**路径参数**:
- `log_id`: 日志 ID (int)

**响应**:
```typescript
interface LogDetail {
  id: number;
  trace_id: string;
  user_name: string;
  endpoint: string;
  method: string;
  status_code: number;
  process_time_ms: number;
  client_ip: string;
  request_params: Record<string, any> | null;  // JSON
  response_body: Record<string, any> | null;   // JSON
  error_message: string | null;
  created_at: string;
}
```

**权限**: 
- 管理员：可查看所有日志
- 普通用户：只能查看自己的日志

**SQL**:
```sql
SELECT 
  id, trace_id, user_name, endpoint, method, 
  status_code, process_time_ms, client_ip, 
  request_params, response_body, error_message, created_at
FROM api_access_logs
WHERE id = :log_id
  AND (is_admin OR user_name = :current_user);
```

---

### 1.3 导出日志

**接口**: `GET /api/portal/audit/logs/export`

**请求参数**:
```typescript
interface ExportParams extends LogQueryParams {
  format?: 'csv' | 'json';  // 默认 csv
}
```

**权限**: 仅管理员

**限制**:
- 单次最多导出 10000 条
- 如果结果超过限制，返回 400 错误

**CSV 格式**:
```csv
ID,Trace ID,User,Method,Endpoint,Status,Response Time (ms),Client IP,Created At
1,abc-123,admin,GET,/api/v1/resources,200,125.5,192.168.1.100,2025-12-27 12:00:00
```

**JSON 格式**:
```json
{
  "export_time": "2025-12-27T12:00:00",
  "total": 1234,
  "items": [...]
}
```

**响应头**:
```
Content-Type: text/csv; charset=utf-8
Content-Disposition: attachment; filename="audit_logs_20251227.csv"
```

---

## 2. 数据库修改

### 2.1 表结构更新

```sql
-- 添加字段
ALTER TABLE api_access_logs 
ADD COLUMN request_params TEXT COMMENT '请求参数(JSON格式)',
ADD COLUMN response_body TEXT COMMENT '响应内容(JSON格式，限制10KB)',
ADD COLUMN error_message TEXT COMMENT '错误信息';

-- 添加索引
CREATE INDEX idx_logs_created_at ON api_access_logs(created_at);
CREATE INDEX idx_logs_status_code ON api_access_logs(status_code);
CREATE INDEX idx_logs_method ON api_access_logs(method);
CREATE INDEX idx_logs_user_name ON api_access_logs(user_name);
CREATE INDEX idx_logs_endpoint ON api_access_logs(endpoint);
```

### 2.2 完整表结构

```sql
CREATE TABLE api_access_logs (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  trace_id VARCHAR(64) NOT NULL,
  user_name VARCHAR(64) NOT NULL,
  endpoint VARCHAR(255) NOT NULL,
  method VARCHAR(10) NOT NULL,
  status_code INT NOT NULL,
  process_time_ms DECIMAL(10,2) NOT NULL,
  client_ip VARCHAR(45),
  request_params TEXT,           -- 新增
  response_body TEXT,             -- 新增
  error_message TEXT,             -- 新增
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_logs_created_at (created_at),
  INDEX idx_logs_status_code (status_code),
  INDEX idx_logs_method (method),
  INDEX idx_logs_user_name (user_name),
  INDEX idx_logs_endpoint (endpoint)
);
```

---

## 3. 中间件修改

### 3.1 AccessLogMiddleware 增强

**文件**: `app/core/middleware.py`

**修改内容**:
```python
class AccessLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        trace_id = str(uuid.uuid4())
        
        # 1. 记录请求参数
        request_params = await self._extract_request_params(request)
        
        # 2. 执行请求
        try:
            response = await call_next(request)
            error_message = None
            
            # 3. 记录响应（仅当状态码 >= 400 或需要调试）
            response_body = None
            if response.status_code >= 400:
                response_body = await self._extract_response_body(response)
                
        except Exception as e:
            error_message = str(e)
            raise
        finally:
            # 4. 保存日志
            process_time_ms = (time.time() - start_time) * 1000
            await self._save_log(
                trace_id=trace_id,
                user_name=user_name,
                endpoint=request.url.path,
                method=request.method,
                status_code=response.status_code,
                process_time_ms=process_time_ms,
                client_ip=request.client.host,
                request_params=request_params,
                response_body=response_body,
                error_message=error_message
            )
        
        return response
    
    async def _extract_request_params(self, request: Request) -> str:
        """提取请求参数（Query + Body）"""
        params = {}
        
        # Query 参数
        if request.url.query:
            params['query'] = dict(request.query_params)
        
        # Body 参数（仅 POST/PUT/PATCH）
        if request.method in ['POST', 'PUT', 'PATCH']:
            try:
                body = await request.body()
                if body:
                    params['body'] = json.loads(body.decode())
                    # 敏感字段脱敏
                    self._mask_sensitive_fields(params['body'])
            except:
                pass
        
        return json.dumps(params, ensure_ascii=False)
    
    def _mask_sensitive_fields(self, data: dict):
        """脱敏敏感字段"""
        sensitive_keys = ['password', 'api_key', 'token', 'secret']
        for key in sensitive_keys:
            if key in data:
                data[key] = '***'
```

---

## 4. 前端 UI 规格

### 4.1 页面布局

```
┌─────────────────────────────────────────────────────────┐
│  审计日志                         [刷新] [导出]          │
├─────────────────────────────────────────────────────────┤
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐               │
│  │总请求│  │成功率│  │平均RT│  │错误数│   统计卡片     │
│  └──────┘  └──────┘  └──────┘  └──────┘               │
├─────────────────────────────────────────────────────────┤
│  筛选条件:                                               │
│  [时间范围▼] [HTTP方法▼] [状态码▼] [用户] [路径] [IP] │
│                                       [清空筛选] [查询]  │
├─────────────────────────────────────────────────────────┤
│  ID │用户│方法│接口路径│状态│耗时│客户端IP│时间│操作  │
│  ───┼────┼────┼────────┼────┼────┼────────┼────┼────  │
│  123│admin│GET│/api/v1/│200│125ms│192...│12:00│详情  │
│  ...                                                     │
├─────────────────────────────────────────────────────────┤
│  第 1 页，共 1234 条    [10/15/20/50/100]  [<] [>]    │
└─────────────────────────────────────────────────────────┘
```

### 4.2 筛选组件

**时间范围选择器**:
- 快捷选项：今天、近7天、近30天
- 自定义：开始日期 - 结束日期

**HTTP 方法多选**:
- [ ] GET
- [ ] POST
- [ ] PUT
- [ ] DELETE
- [ ] PATCH

**状态码多选**:
- [ ] 2xx (成功)
- [ ] 4xx (客户端错误)
- [ ] 5xx (服务器错误)
- 或自定义状态码

### 4.3 详情对话框

```
┌────────────────────────────────────────┐
│  日志详情                       [关闭] │
├────────────────────────────────────────┤
│  基本信息:                              │
│  Trace ID: abc-123-def                 │
│  用户: admin                            │
│  方法: GET                              │
│  路径: /api/v1/resources               │
│  状态码: 200                            │
│  响应时间: 125.5 ms                     │
│  客户端IP: 192.168.1.100               │
│  时间: 2025-12-27 12:00:00             │
├────────────────────────────────────────┤
│  请求参数:                              │
│  {                           [复制]    │
│    "query": {...},                     │
│    "body": {...}                       │
│  }                                      │
├────────────────────────────────────────┤
│  响应内容:                              │
│  {                           [复制]    │
│    "code": 200,                        │
│    "data": {...}                       │
│  }                                      │
└────────────────────────────────────────┘
```

---

## 5. 组件设计

### 5.1 筛选栏组件 (FilterBar.vue)

```vue
<template>
  <div class="filter-bar">
    <DateRangePicker v-model="filters.dateRange" />
    <MultiSelect v-model="filters.methods" :options="methodOptions" />
    <StatusCodeFilter v-model="filters.statusCodes" />
    <Input v-model="filters.userName" placeholder="用户名" />
    <Input v-model="filters.endpoint" placeholder="接口路径" />
    <Input v-model="filters.clientIp" placeholder="客户端IP" />
    <Button @click="clearFilters">清空</Button>
    <Button @click="search" type="primary">查询</Button>
  </div>
</template>
```

### 5.2 统计卡片 (StatisticsCards.vue)

```vue
<template>
  <div class="grid grid-cols-4 gap-4">
    <StatCard title="总请求数" :value="stats.total" icon="📊" />
    <StatCard 
      title="成功率" 
      :value="`${stats.successRate}%`" 
      :color="stats.successRate > 90 ? 'green' : 'red'" 
    />
    <StatCard title="平均响应时间" :value="`${stats.avgRT}ms`" />
    <StatCard title="错误数" :value="stats.errors" color="red" />
  </div>
</template>
```

### 5.3 详情对话框 (LogDetailDialog.vue)

```vue
<template>
  <Dialog v-model="visible" title="日志详情">
    <div class="detail-content">
      <Section title="基本信息">
        <InfoItem label="Trace ID" :value="log.trace_id" />
        <!-- ... -->
      </Section>
      
      <Section title="请求参数">
        <JsonViewer :data="log.request_params" />
        <Button @click="copyToClipboard(log.request_params)">复制</Button>
      </Section>
      
      <Section title="响应内容">
        <JsonViewer :data="log.response_body" />
        <Button @click="copyToClipboard(log.response_body)">复制</Button>
      </Section>
    </div>
  </Dialog>
</template>
```

---

## 6. 测试用例

### 6.1 后端测试

```python
# test_audit_enhanced.py

async def test_filter_by_time_range():
    """测试时间范围筛选"""
    response = await client.get(
        "/api/portal/audit/logs",
        params={
            "start_time": "2025-12-27T00:00:00",
            "end_time": "2025-12-27T23:59:59"
        },
        headers={"X-API-Key": admin_key}
    )
    assert response.status_code == 200
    # 验证返回的日志时间都在范围内

async def test_filter_by_method():
    """测试HTTP方法筛选"""
    response = await client.get(
        "/api/portal/audit/logs",
        params={"method": "GET"},
        headers={"X-API-Key": admin_key}
    )
    assert response.status_code == 200
    assert all(log["method"] == "GET" for log in response.json()["items"])

async def test_log_detail_access():
    """测试日志详情访问权限"""
    # 管理员可以查看任何日志
    # 普通用户只能查看自己的日志

async def test_export_csv():
    """测试CSV导出"""
    response = await client.get(
        "/api/portal/audit/logs/export",
        params={"format": "csv"},
        headers={"X-API-Key": admin_key}
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv"
```

---

## 7. 性能优化

### 7.1 数据库优化
- ✅ 添加组合索引 `(created_at, status_code)`
- ✅ 定期归档旧数据（如 3 个月前）
- ✅ 考虑分表策略（按月分表）

### 7.2 查询优化
- ✅ 限制默认时间范围（最近 7 天）
- ✅ 导出限制最多 10000 条
- ✅ 响应内容限制大小（10KB）

### 7.3 缓存策略
- ✅ 统计数据缓存 5 分钟
- ✅ 日志列表缓存 1 分钟

---

## 8. 安全考虑

### 8.1 权限控制
- ✅ 仅管理员可查看所有日志
- ✅ 普通用户只能查看自己的日志
- ✅ 导出功能限制为管理员

### 8.2 数据脱敏
- ✅ 密码、API Key、Token 等敏感字段自动脱敏
- ✅ 响应内容截断，避免泄露大量数据

### 8.3 日志保留
- ✅ 定期清理旧日志（建议保留 3-6 个月）
- ✅ 重要日志归档存储
