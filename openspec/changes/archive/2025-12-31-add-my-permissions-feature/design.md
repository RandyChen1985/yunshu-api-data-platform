# 设计文档: Dashboard "我的权限"

## 1. API 设计

### `GET /api/portal/dashboard/my-resources`

**Request**:
- Headers: `X-API-Key`

**Response**:
```json
{
  "code": 200,
  "data": [
    {
      "resource_key": "donghuan_real_metrics",
      "resource_name": "动环实时指标",
      "resource_group": "动环系统",
      "updated_at": "2024-05-20 12:00:00", # 元数据更新时间
      "remarks": "这是一段备注",
      "fields_config": [
          {"name": "metric_value", "description": "指标值", "type": "Float64"}
      ],
      "api_url": "/api/v1/resources/donghuan_real_metrics"
    }
  ]
}
```

## 2. UI 设计

### 2.1 Header 入口
- 位置: 右上角，`Online Users` 左侧。
- 样式: 带图标（如 `ViewGridIcon` 或 `KeyIcon`），文字 "我的权限(9)"。
- 状态: 加载中显示 Spinner，加载完显示数字。

### 2.2 权限列表弹窗 (Modal)
- 标题: "我的资源权限"
- 内容区: 滚动列表。
- 列表项 (Card 样式):
    - **Header**: 资源名 (中文) + ID (英文, 可复制) + Group Tag.
    - **Body**: 
        - 备注 (Tooltip).
        - "字段详情" 按钮 -> Popover 显示字段表格.
        - "调用示例" 按钮 -> Modal 显示代码.
    - **Footer**: 更新时间.

### 2.3 调用示例弹窗
- Tab 1: **通用调用**
    ```bash
    curl -X POST .../api/v1/query -d '{"resource": "..."}'
    ```
- Tab 2: **接口调用**
    ```bash
    curl -X GET .../api/v1/resources/...
    ```

## 3. 交互流程
1. 用户登录 Dashboard。
2. `Dashboard.vue` `onMounted` 调用 `fetchMyResources` 获取列表。
3. 计算列表长度 -> 更新 Header 数字。
4. 用户点击 Header 按钮 -> 打开 Modal。
