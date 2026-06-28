# Change: Refactor ClickHouseAdapter for SQL Parameterization (SQL参数化重构)

## Why
现有 `ClickHouseAdapter` 使用手动字符串拼接和转义，存在 SQL 注入风险。为了提高系统安全性，需要重构为使用 `asynch` 驱动的原生参数绑定机制。

## What Changes
- 重构 `app/services/data_adapter/clickhouse.py` 中的 `_build_where`, `execute`, `execute_summary` 方法。
- 移除不安全的 `_escape` 方法。
-修复部分比较操作符 (`>`, `<`, `!=`) 缺失的问题。
- 增加完整的单元测试覆盖。

## Impact
- Affected specs: `adapter`
- Affected code: `app/services/data_adapter/clickhouse.py`
