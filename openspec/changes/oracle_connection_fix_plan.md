# Oracle 连接逻辑改进计划 (Oracle Connection Logic Improvement Plan)

## 1. 为什么这么做 (Why)

目前的 Oracle 连接实现在高并发和异步环境下存在几个关键缺陷：
- **核心 Bug**：`_create_oracle_pool` 中缺失 `await`，导致返回的是协程对象而非连接池，这会直接导致所有 Oracle 查询在运行时报错。
- **稳定性风险**：厚模式（Thick Mode）初始化逻辑分散且存在重复调用风险，可能导致 `DPY-2053` 错误（模式已设置）。
- **资源泄露**：连接池关闭逻辑不够稳健，未完全适配 `python-oracledb` 的异步 API。
- **功能限制**：DSN 构造过于简单，无法支持复杂的 Oracle 连接场景。

## 2. 准备怎么搞 (How)

### 阶段 1：修复核心 Bug
- 在 `app/services/pool_manager.py` 的 `_create_oracle_pool` 中添加缺失的 `await`。
- 确保所有 `pool.acquire()` 和 `pool.close()` 的调用都符合异步规范。

### 阶段 2：重构初始化与模式管理
- 统一 `init_oracle_thick_mode` 的触发时机。
- 移除无效的模块重载逻辑 (`force_reset_oracle_mode`)。
- 优化厚模式下的 Instant Client 路径探测逻辑。

### 阶段 3：增强 DSN 支持
- 允许用户提供更灵活的连接字符串。

## 3. 为什么这么修改 (Rationale)

- **正确性**：`python-oracledb` 2.x 的异步 API 要求明确的协程调度，修正 `await` 是保证程序运行的基础。
- **鲁棒性**：集中管理模式初始化可以避免 Oracle 驱动最常见的冲突错误。
- **可维护性**：移除无效代码（如 reload 逻辑）并简化流程，降低后续排查难度。

## 4. 详细修改列表

- `app/services/pool_manager.py`:
    - 修正 `_create_oracle_pool`。
    - 优化 `init_oracle_thick_mode`。
    - 修正 `invalidate_pool`。
- `app/services/data_adapter/oracle.py`:
    - 确保 `execute` 方法中的异步上下文管理器使用正确。
- `app/api/portal/endpoints/datasource.py`:
    - 修正测试连接接口中的调用方式。
