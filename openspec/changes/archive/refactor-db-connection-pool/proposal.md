# Change: Refactor ClickHouse Connection to Use Pool

## Why
原有的 ClickHouse 连接方式为每次请求创建一个新的 TCP 连接 (`Connection`)，在高并发场景下会导致：
1.  频繁握手增加延迟。
2.  大量 `TIME_WAIT` 状态可能耗尽服务器端口资源。
3.  无法控制最大并发连接数，存在压垮数据库的风险。

## What Changes
-   **引入连接池**: 使用 `asynch.pool.Pool` 替换直接的 `Connection` 实例化。
-   **生命周期管理**: 在 FastAPI `lifespan` 中统一管理连接池的初始化 (`startup`/`init`) 和销毁 (`shutdown`)。
-   **调用方式变更**: 将 `get_clickhouse_connection` 改造为异步上下文管理器，支持 `async with` 自动归还连接。

## Impact
-   **Affected Specs**: Architecture / Database Access Patterns
-   **Affected Code**: 
    -   `app/core/database.py` (Core logic)
    -   `app/main.py` (Lifespan)
    -   `app/services/data_adapter.py` (Consumer)
