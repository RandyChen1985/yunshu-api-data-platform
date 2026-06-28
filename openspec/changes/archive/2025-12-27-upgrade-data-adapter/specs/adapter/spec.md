## ADDED Requirements

### Requirement: 多源数据适配支持 (Multi-Source Support)
系统必须 (MUST) 提供可插拔的适配器层，通过统一接口为多种数据源（ClickHouse, MySQL, HBase）提供支持 (SHALL support)。

#### Scenario: 获取 ClickHouse 适配器
- **WHEN** 系统请求 "clickhouse" 类型的适配器
- **THEN** 返回 `ClickHouseAdapter` 的实例
- **AND** 该适配器实现了 `execute` 和 `execute_summary` 方法。

#### Scenario: 执行通用查询
- **WHEN** 对任何适配器调用 `execute` 方法并传入有效的 `LogicalQuery`
- **THEN** 返回标准化的 `ResultSet` 结果集。

#### Scenario: 未知数据源
- **WHEN** 系统请求一种未知的数据源类型（例如 "mongo"）
- **THEN** 抛出 `NotImplementedError` 或 `ValueError` 异常。
