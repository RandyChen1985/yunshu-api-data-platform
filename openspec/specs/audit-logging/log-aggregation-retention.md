# 日志聚合与生命周期管理 (Log Aggregation & Retention)

## 1. 背景与目标
当前 `api_access_logs` 表数据量已达 500万+，直接基于原始日志进行 Dashboard 统计导致查询缓慢。同时，无限制的日志增长会导致存储压力和维护困难。

**目标**：
1.  **预聚合**：建立分钟级统计表，Dashboard 改为从统计表读取数据，实现毫秒级响应。
2.  **生命周期管理**：自动清理 7 天前的原始访问日志，控制表大小。
3.  **历史保留**：聚合后的统计数据保留 90 天（或更久），用于长期趋势分析。

## 2. 数据库设计 (Schema Design)

### 2.1 新增聚合表 `api_access_stats_1m`
用于存储每分钟的聚合指标。

```sql
CREATE TABLE api_access_stats_1m (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    time_bucket DATETIME NOT NULL COMMENT '时间桶（分钟级，如 2026-01-23 10:01:00）',
    
    -- 维度 (Dimensions)
    user_name VARCHAR(64) DEFAULT 'ALL' COMMENT '用户名 (ALL表示全局统计)',
    endpoint VARCHAR(255) DEFAULT 'ALL' COMMENT '接口路径',
    method VARCHAR(10) DEFAULT 'ALL' COMMENT 'HTTP方法',
    status_code INT DEFAULT 0 COMMENT '状态码',
    
    -- 指标 (Metrics)
    total_calls INT NOT NULL DEFAULT 0 COMMENT '调用总数',
    total_error INT NOT NULL DEFAULT 0 COMMENT '错误总数(status>=400)',
    avg_latency FLOAT NOT NULL DEFAULT 0 COMMENT '平均耗时(ms)',
    max_latency FLOAT NOT NULL DEFAULT 0 COMMENT '最大耗时(ms)',
    p95_latency FLOAT DEFAULT 0 COMMENT 'P95耗时(预留)',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 索引设计
    UNIQUE KEY uk_bucket_dims (time_bucket, user_name, endpoint, method, status_code),
    INDEX idx_time (time_bucket)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='API访问日志分钟级聚合表';
```

## 3. 定时任务逻辑 (Scheduled Tasks)

我们需要引入调度框架（如 `APScheduler`）来执行后台任务。

### 3.1 聚合任务 (Aggregator)
*   **频率**：每 1 分钟执行一次 (Cron: `*/1 * * * *`)。
*   **延迟处理**：每次执行统计 **"2分钟前"** 的数据，以防止日志写入延迟导致统计不全。
*   **聚合维度**：
    1.  **全局趋势**：`GROUP BY time_bucket`
    2.  **接口级趋势**：`GROUP BY time_bucket, endpoint` (可选，视数据量而定)
    3.  **用户级趋势**：`GROUP BY time_bucket, user_name`
*   **SQL 逻辑**：
    ```sql
    INSERT INTO api_access_stats_1m (...)
    SELECT 
        DATE_FORMAT(created_at, '%Y-%m-%d %H:%i:00') as bucket,
        user_name,
        endpoint,
        method,
        status_code,
        COUNT(*) as total,
        SUM(CASE WHEN status_code >= 400 THEN 1 ELSE 0 END) as errors,
        AVG(process_time_ms) as avg_lat,
        MAX(process_time_ms) as max_lat
    FROM api_access_logs
    WHERE created_at >= [Start Time] AND created_at < [End Time]
    GROUP BY bucket, user_name, endpoint, method, status_code;
    ```

### 3.2 清理任务 (Cleaner)
*   **频率**：每天凌晨 03:00 执行 (Cron: `0 3 * * *`)。
*   **逻辑**：
    *   删除 `created_at < NOW() - 7 DAYS` 的原始日志。
    *   **注意**：为了避免锁表，应采用分批删除（Chunk Delete），例如每次删除 5000 条，循环执行直到删完。

## 4. Dashboard 改造 (Dashboard Refactoring)

Dashboard 接口需要修改查询源：

| 接口 | 当前源 | 新源 | 逻辑变更 |
| :--- | :--- | :--- | :--- |
| `/admin-stats` (Trends) | `api_access_logs` | `api_access_stats_1m` | 直接 SUM(total_calls) where time_bucket >= ? |
| `/api-trends` | `api_access_logs` | `api_access_stats_1m` | 按天 Group By 统计表 |
| `/api-trends-24h` | `api_access_logs` | `api_access_stats_1m` | 按小时 Group By 统计表 |
| `/recent-activities` | `api_access_logs` | `api_access_logs` | **保持不变** (仍需查最新原始记录) |

## 6. UI/UX 改进计划 (UI/UX Design Improvements)

### 6.1 概览页升级 (Dashboard Enhancements)
利用聚合表的高性能特性，前端展示将不再局限于简单的调用次数。
*   **性能趋势图**：新增 "API 平均响应时间 (ms)" 趋势图，与调用量趋势图并列展示。
*   **异常监控**：新增 "错误率 (Error Rate)" 趋势图。
*   **Top 榜单**：
    *   **最慢接口 Top 5**：基于 `avg_latency` 排序。
    *   **最多错误接口 Top 5**：基于 `total_error` 排序。

### 6.2 新增：日志管理面板 (Log Management UI)
在“系统管理”模块下新增 **[日志维护]** 标签页。

#### 界面元素：
1.  **存储概览 (Storage Stats)**：
    *   原始日志：行数 (e.g., "5.2M") / 预估大小 (e.g., "1.2GB") / 保留策略 (e.g., "7 Days")。
    *   聚合数据：行数 (e.g., "50K") / 预估大小 (e.g., "5MB") / 保留策略 (e.g., "90 Days")。

2.  **配置区域 (Configuration)**：
    *   `Raw Log Retention (Days)`: 输入框 (Stepper)，允许修改清理阈值。
    *   `Stats Retention (Days)`: 输入框 (Stepper)。
    *   *注：修改配置将实时更新到后端系统配置表或 Redis。*

3.  **运维操作 (Actions)**：
    *   **[立即清理 (Purge Now)]**：手动触发清理任务，带确认弹窗。
    *   **[重新聚合 (Re-aggregate)]**：允许指定日期范围，重新生成聚合数据（用于修复或回填数据）。

## 7. 实施计划 (Implementation Plan)

1.  **依赖安装**：引入 `APScheduler`。
2.  **数据库变更**：创建聚合表。
3.  **任务开发**：在 `app/jobs/` 下实现聚合与清理逻辑。
4.  **服务集成**：在 `main.py` 启动时初始化 Scheduler。
5.  **接口切换**：修改 Dashboard 查询逻辑，适配新表。
6.  **前端开发**：实现新的图表组件和日志管理配置页。
