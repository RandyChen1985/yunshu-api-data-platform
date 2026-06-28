# adapter Specification

## Purpose
TBD - created by archiving change upgrade-data-adapter. Update Purpose after archive.
## Requirements
### Requirement: 多源数据适配支持 (Multi-Source Support)
系统必须 (MUST) 提供可插拔的适配器层，通过统一接口为多种数据源（ClickHouse, MySQL, Oracle）提供支持 (SHALL support)。适配器必须能够基于动态配置的数据源连接信息进行实例化。

#### Scenario: 获取 ClickHouse 适配器
- **WHEN** 系统指定一个 ClickHouse 类型的数据源 ID
- **THEN** 返回绑定了该数据源连接池的 `ClickHouseAdapter` 实例。

#### Scenario: 获取 MySQL 适配器
- **WHEN** 系统指定一个 MySQL 类型的数据源 ID
- **THEN** 返回绑定了该数据源连接池的 `MySQLAdapter` 实例。

### Requirement: SQL 安全执行 (SQL Security Execution)
所有 SQL 类型的适配器（如 ClickHouse）必须 (MUST) 使用参数化查询 (Parameterized Queries) 或驱动级参数绑定来防止 SQL 注入。

#### Scenario: 禁止手动拼接
- **WHEN** 执行带有用户输入的过滤条件查询
- **THEN** 适配器通过 `{param}` 或 `%s` 占位符传递参数
- **AND** 不直接在 SQL 字符串中进行值的拼接。

#### Scenario: 操作符支持
- **WHEN** 过滤条件包含 `>`, `<`, `=`, `!=`, `IN` 等操作符
- **THEN** 生成的 SQL 正确包含相应操作符且参数被安全绑定。

### Requirement: 动态连接池管理 (Dynamic Pool Management)
系统必须 (MUST) 维护一个缓存池，用于管理不同物理数据源的长连接，避免频繁创建连接。

#### Scenario: 惰性初始化
- **WHEN** 第一次请求某个数据源的连接
- **THEN** 创建对应连接池并存入缓存。

#### Scenario: 配置变更销毁
- **WHEN** 数据源连接信息被修改或删除
- **THEN** 对应连接池必须立即销毁以释放资源。

