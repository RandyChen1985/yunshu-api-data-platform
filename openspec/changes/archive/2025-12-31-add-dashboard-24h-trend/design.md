# 设计: Dashboard 24小时趋势可视化

## 架构决策
### 1. 技术栈选择: ECharts
- **原因**: ECharts 提供了丰富的图表类型，对大数据量处理性能好，且配置项极其灵活。
- **集成方式**: 使用 `echarts` 和 `vue-echarts`。

### 2. 后端聚合策略
- **数据源**: `api_access_logs` 表。
- **聚合维度**: 小时级。
- **时间范围**: 固定为过去 24 小时。
- **连续性保障**: 使用 Python 构建 24 小时的时间模板，将数据库查询结果填入，确保即使某小时没有请求，图表上也会显示 0。

## 详细设计

### 后端 API 实现
- **接口名称**: `get_api_trends_24h`
- **逻辑**:
  1. 获取当前时间 `now` 和昨天此时 `start_time`。
  2. SQL:
     ```sql
     SELECT 
         DATE_FORMAT(created_at, '%Y-%m-%d %H:00:00') as hour,
         COUNT(*) as total_calls,
         SUM(CASE WHEN status_code >= 200 AND status_code < 300 THEN 1 ELSE 0 END) as success_calls
     FROM api_access_logs
     WHERE created_at >= %s
     GROUP BY hour
     ORDER BY hour ASC
     ```
  3. 后处理: 将结果映射到一个包含 24 小时完整时间序列的字典中。

### 前端 UI 实现
- **组件位置**: `Overview.vue` 中 `Statistics Cards` 下方。
- **图表配置**:
  - **类型**: 折线图 (Line) 带阴影面积 (Area)。
  - **X轴**: 时间 (HH:00)。
  - **Y轴**: 请求数。
  - **系列**: 
    - 总请求量 (蓝色)
    - 成功请求量 (绿色)
- **响应式**: 自适应容器宽度。

## 数据库考虑
- `api_access_logs` 的 `created_at` 字段必须有索引。
- 考虑到这是一个 Dashboard 接口，调用频率不高且数据量受限（仅 24 小时），直接聚合性能可以接受。

## 接口定义 (OpenAPI)
```yaml
/api/portal/dashboard/api-trends-24h:
  get:
    summary: 获取近24小时API请求趋势
    responses:
      200:
        description: 成功的响应
        content:
          application/json:
            schema:
              type: array
              items:
                type: object
                properties:
                  hour: { type: string, example: "10:00" }
                  total_calls: { type: integer }
                  success_calls: { type: integer }
```
