# 系统容错与重试机制规格书 (Resilience & Retry Spec)

## 1. 概述
为了提高系统在数据库闪断、网络抖动等不稳定环境下的可用性，本变更引入了基于 `tenacity` 的重试机制，并增强了全局异常处理。

## 2. 核心变更

### 2.1 数据库连接初始化重试
- **位置**: `app/core/database.py`
- **逻辑**: 在系统启动初始化 `mysql_pool` 和 `clickhouse_pool` 时，如果发生任何异常，将自动重试。
- **策略**:
    - **最大重试次数**: 3 次
    - **等待策略**: 指数退避 (Wait Exponential)，1s -> 2s -> 4s ... (最大 10s)
    - **日志**: 每次重试前记录 Warning 日志。

### 2.2 ClickHouse 查询重试
- **位置**: `app/services/data_adapter/clickhouse.py`
- **逻辑**: 在执行 `execute` 和 `execute_summary` 时，针对特定的网络/连接错误进行重试。
- **捕获异常**:
    - `asynch.errors.InterfaceError` (连接丢失)
    - `OSError` (底层 Socket 错误)
- **策略**:
    - **最大重试次数**: 3 次
    - **等待策略**: 快速指数退避，0.5s -> 1s ... (最大 5s)，以减少对用户请求延迟的影响。

### 2.3 全局异常处理
- **位置**: `app/main.py`
- **逻辑**: 添加了针对 `InterfaceError` (ClickHouse) 和 `OperationalError` (MySQL) 的全局异常处理器。
- **响应**:
    - **状态码**: `503 Service Unavailable`
    - **响应体**: `{ "code": 503, "message": "Service Temporarily Unavailable..." }`
    - **Header**: `Retry-After: 30`

## 3. 验证
- **自动化测试**: 现有测试套件 (66个用例) 全部通过，确保引入 `retry` 装饰器后没有破坏原有逻辑。
