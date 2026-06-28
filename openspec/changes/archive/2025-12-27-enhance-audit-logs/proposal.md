# 提案：审计日志页面功能增强

## 1. 背景与动机

当前审计日志页面 (`AuditLogs.vue`) 功能较为简单，仅提供基础的日志列表查看和分页功能。为了提升管理员的运维效率和系统的可观测性，需要增强审计日志功能。

### 当前问题
- ❌ 缺少筛选条件（时间范围、HTTP 方法、状态码、用户）
- ❌ 无法查看日志详情（请求参数、响应内容、错误信息）
- ❌ 无法导出日志用于离线分析
- ❌ 每页固定 20 条，无法调整
- ❌ 没有统计概览（成功率、平均响应时间）
- ❌ 客户端 IP 字段未展示

## 2. 目标

### 2.1 核心目标
1. **高级筛选**：支持多维度筛选（时间范围、方法、状态码、用户、接口路径）
2. **日志详情**：点击查看完整的请求和响应信息
3. **数据导出**：支持 CSV/JSON 格式导出筛选后的日志
4. **可配置分页**：支持每页 10/15/20/50/100 条切换
5. **统计概览**：显示关键指标（总请求数、成功率、平均响应时间、错误数）

### 2.2 改进方向
- 提升数据可读性（格式化时间、高亮错误）
- 优化用户体验（快速筛选、实时搜索）
- 增强分析能力（导出、统计）

## 3. 技术方案

### 3.1 后端改进

#### 3.1.1 API 增强
**接口**: `GET /api/portal/audit/logs`

**新增查询参数**:
```python
- start_time: Optional[str]     # 开始时间 (ISO格式)
- end_time: Optional[str]       # 结束时间 (ISO格式)
- method: Optional[str]          # HTTP方法 (GET/POST/PUT/DELETE/PATCH)
- status_code: Optional[int]     # 状态码 (200/400/500等)
- min_status: Optional[int]      # 最小状态码 (范围查询)
- max_status: Optional[int]      # 最大状态码 (范围查询)
- endpoint: Optional[str]        # 接口路径 (模糊匹配)
- user_name: Optional[str]       # 用户名 (已存在，保留)
- client_ip: Optional[str]       # 客户端IP
```

**响应增强**:
```json
{
  "total": 1234,
  "page": 1,
  "size": 20,
  "items": [...],
  "statistics": {
    "total_requests": 1234,
    "success_count": 1100,
    "error_count": 134,
    "success_rate": 89.14,
    "avg_response_time": 125.5
  }
}
```

#### 3.1.2 新增日志详情接口
**接口**: `GET /api/portal/audit/logs/{log_id}`

**响应**:
```json
{
  "id": 123,
  "trace_id": "abc-123-def",
  "user_name": "admin",
  "endpoint": "/api/v1/resources",
  "method": "GET",
  "status_code": 200,
  "process_time_ms": 125.5,
  "client_ip": "192.168.1.100",
  "request_params": {...},
  "response_body": {...},
  "error_message": null,
  "created_at": "2025-12-27T12:00:00"
}
```

**注意**: 需要在数据库表 `api_access_logs` 中添加字段：
- `request_params` TEXT (存储 JSON)
- `response_body` TEXT (存储 JSON，大数据考虑截断)
- `error_message` TEXT

#### 3.1.3 导出功能
**接口**: `GET /api/portal/audit/logs/export`

**查询参数**: 与列表接口相同

**响应**: 
- CSV 格式（Content-Type: text/csv）
- JSON 格式（Content-Type: application/json）

**限制**: 
- 单次最多导出 10000 条
- 管理员专用

### 3.2 前端改进

#### 3.2.1 筛选栏
- 时间范围选择器（快捷选项：今天、近7天、近30天、自定义）
- HTTP 方法多选（GET/POST/PUT/DELETE/PATCH）
- 状态码多选（200/400/404/500 等常用状态码）
- 用户名搜索框（支持模糊匹配）
- 接口路径搜索框（支持模糊匹配）
- 客户端 IP 搜索框

#### 3.2.2 统计卡片
顶部展示 4 个统计卡片：
1. 总请求数
2. 成功率（绿色/红色渐变）
3. 平均响应时间
4. 错误数量

#### 3.2.3 表格增强
- 添加"客户端 IP"列
- 添加"详情"操作按钮
- 状态码颜色区分（2xx 绿色、4xx 黄色、5xx 红色）
- 响应时间区分（<100ms 绿色、100-500ms 黄色、>500ms 红色）

#### 3.2.4 日志详情对话框
- 展示完整的请求和响应信息
- JSON 格式化显示
- 支持复制内容
- 显示 trace_id 用于日志追踪

#### 3.2.5 导出功能
- 右上角添加"导出"按钮
- 支持选择格式（CSV/JSON）
- 应用当前筛选条件
- 显示导出进度

#### 3.2.6 分页配置
- 支持每页条数切换（10/15/20/50/100）
- 显示总页数和当前页
- 跳转到指定页功能

### 3.3 数据库改进

#### 3.3.1 表结构修改
```sql
ALTER TABLE api_access_logs 
ADD COLUMN request_params TEXT COMMENT '请求参数(JSON)',
ADD COLUMN response_body TEXT COMMENT '响应内容(JSON)',
ADD COLUMN error_message TEXT COMMENT '错误信息';

-- 添加索引优化查询
CREATE INDEX idx_created_at ON api_access_logs(created_at);
CREATE INDEX idx_status_code ON api_access_logs(status_code);
CREATE INDEX idx_method ON api_access_logs(method);
CREATE INDEX idx_user_name ON api_access_logs(user_name);
```

#### 3.3.2 中间件修改
更新 `app/core/middleware.py` 中的 `AccessLogMiddleware`：
- 记录请求参数（Query/Body）
- 记录响应内容（考虑大小限制，如最多 10KB）
- 捕获异常信息

## 4. 实现计划

### 阶段一：后端增强（优先级 P0）
1. 数据库表结构修改
2. 更新 AccessLogMiddleware 记录更多信息
3. 增强 `GET /api/portal/audit/logs` 接口（添加筛选参数）
4. 实现 `GET /api/portal/audit/logs/{log_id}` 详情接口
5. 实现 `GET /api/portal/audit/logs/export` 导出接口

### 阶段二：前端增强（优先级 P0）
1. 实现筛选栏组件
2. 实现统计卡片
3. 更新表格（添加客户端IP列、详情按钮）
4. 实现日志详情对话框
5. 实现分页配置功能

### 阶段三：优化（优先级 P1）
1. 实现导出功能
2. 添加自动刷新功能
3. 性能优化（查询缓存、索引优化）
4. 编写测试用例

## 5. 验收标准

1. ✅ 支持多维度筛选（时间、方法、状态码、用户、路径、IP）
2. ✅ 点击日志可查看完整详情（请求、响应、错误）
3. ✅ 支持导出 CSV/JSON 格式
4. ✅ 显示统计概览（总数、成功率、响应时间、错误数）
5. ✅ 支持调整每页显示条数（10/15/20/50/100）
6. ✅ 表格显示客户端 IP
7. ✅ 所有接口通过自动化测试
8. ✅ 页面响应流畅，无明显卡顿
9. ✅ 错误信息友好展示（Toast 通知）

## 6. 风险与考虑

### 6.1 性能风险
- **问题**: 大量日志数据可能导致查询缓慢
- **方案**: 
  - 添加数据库索引
  - 限制时间范围（默认最近7天）
  - 分页查询
  - 考虑定期归档旧日志

### 6.2 存储风险
- **问题**: 记录完整请求/响应会快速增长数据库
- **方案**:
  - 响应内容限制大小（如 10KB）
  - 定期清理旧数据（如保留最近 3 个月）
  - 敏感数据脱敏（密码、密钥等）

### 6.3 安全风险
- **问题**: 日志可能包含敏感信息
- **方案**:
  - 仅管理员可查看完整日志
  - 普通用户只能查看自己的日志
  - 导出功能限制为管理员
  - 敏感字段脱敏处理

## 7. 后续优化

1. **实时监控**: WebSocket 实时推送新日志
2. **日志分析**: 统计报表、趋势图表
3. **告警功能**: 错误率超过阈值时告警
4. **日志聚合**: 按接口、用户、时间段聚合统计
5. **搜索优化**: 全文搜索、正则匹配

## 8. 预估工作量

- **后端开发**: 8-10 小时
- **前端开发**: 10-12 小时
- **测试**: 3-4 小时
- **总计**: 21-26 小时
