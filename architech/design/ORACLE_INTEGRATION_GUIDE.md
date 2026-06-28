# Oracle 数据库集成与适配指南 (Oracle Integration Guide)

本指南旨在解决在 FastAPI (异步) 环境下对接 Oracle 数据库（特别是 Oracle 11g 及以下版本）时遇到的模式冲突、性能阻塞及驱动限制问题。

---

## 1. 核心技术选型：Thin vs Thick Mode

`python-oracledb` 提供两种工作模式。在对接旧版数据库（如 Oracle 11g）时，必须明确两者的限制：

| 特性 | **薄模式 (Thin Mode)** | **厚模式 (Thick Mode)** |
| :--- | :--- | :--- |
| **库依赖** | 纯 Python，无需 Instant Client | **必须安装 Oracle Instant Client** |
| **异步支持** | **原生支持 `async/await`** | **不支持异步 API** (核心冲突点) |
| **数据库版本** | 建议 Oracle 12.1+ | **支持 Oracle 11.2+** |
| **并发模型** | 协程非阻塞 | 线程阻塞 (需手动异步化) |

> **结论**：若目标数据库为 Oracle 11g，**必须启用厚模式**，且代码层必须使用**同步驱动 + 线程包装**。

---

## 2. 环境配置 (以 Docker 为例)

### 2.1 环境变量与挂载
厚模式需要系统能找到 Oracle 客户端库文件。

```yaml
# docker-compose.yml 示例
services:
  api:
    environment:
      - USE_ORACLE_THICK_MODE=1
      - LD_LIBRARY_PATH=/opt/oracle/instantclient  # Linux 必须通过环境变量设置
    volumes:
      - /path/to/host/instantclient_19_30:/opt/oracle/instantclient
```

---

## 3. 核心代码实现

### 3.1 规避 DPY-2053 错误 (模式冲突)
**报错原因**：在一个进程中先启用了厚模式（调用了 `init_oracle_client`），随后又调用了异步创建方法（如 `create_pool_async`），驱动会因模式冲突报错。

**解决方案**：在厚模式下强制使用**同步连接池**。

```python
# pool_manager.py 逻辑参考
if os.environ.get("USE_ORACLE_THICK_MODE") == "1":
    # 1. 厚模式初始化 (全局仅一次)
    oracledb.init_oracle_client(lib_dir="/opt/oracle/instantclient")
    
    # 2. 强制使用同步连接池
    pool = oracledb.create_pool(
        user=user, password=pwd, dsn=dsn, min=1, max=50
    )
else:
    # 薄模式使用异步池
    pool = await oracledb.create_pool_async(...)
```

### 3.2 异步环境下安全调用 (避免阻塞)
由于厚模式不支持 `await`，直接调用会阻塞 FastAPI 的事件循环。必须使用 `asyncio.to_thread` 调度到线程池。

```python
# adapter/oracle.py 逻辑参考
import asyncio

async def execute_query(pool, sql, params):
    # 将同步的 acquire 和 execute 包装在线程中
    def sync_op():
        with pool.acquire() as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                return cursor.fetchall()
    
    # 非阻塞执行
    return await asyncio.to_thread(sync_op)
```

---

## 4. 常见问题排查 (Troubleshooting)

### 4.1 DPI-1047: Cannot locate a 64-bit Oracle Client library
*   **Linux**：`init_oracle_client(lib_dir=...)` 参数在 Linux 下无效。必须确保 `LD_LIBRARY_PATH` 环境变量在进程启动前已设置，且包含 `.so` 文件。
*   **依赖缺失**：运行 `ldd libclntsh.so` 检查是否缺少 `libaio1`。若缺少，请运行 `apt-get install libaio1`。

### 4.2 DPY-2053: Thin mode cannot be used because thick mode has already been enabled
*   **检查点**：代码中是否使用了带 `_async` 后缀的方法？
*   **修正**：厚模式下，请将所有 `create_pool_async` 改为 `create_pool`，`connect_async` 改为 `connect`。

---

## 5. 项目中的具体应用 (Checklist)

1. [ ] **依赖检查**：`requirements.txt` 中包含 `oracledb`。
2. [ ] **初始化**：在 `app/main.py` 或连接池管理类中统一初始化 `init_oracle_client`。
3. [ ] **类型探测**：在操作数据库前通过 `asyncio.iscoroutinefunction(pool.acquire)` 探测池类型。
4. [ ] **线程隔离**：所有厚模式操作必须包裹在 `asyncio.to_thread` 中。

---
*文档更新日期：2026-03-05*
