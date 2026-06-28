## Context
系统需要支持多种类型的数据库作为数据源，且这些数据源需要能够动态增删改查。

## Decisions

### 1. Connection Pool Management
引入 `DataSourcePoolManager` 类（Singleton），内部维护 `dict[int, Pool]`。
- 键为 `sys_data_source` 的 `id`。
- 值为对应的协议连接池（`asynch.Pool` 或 `aiomysql.Pool`）。
- 连接池在第一次使用时惰性初始化。

### 2. MySQL Adapter Implementation
`MySQLAdapter` 将继承 `DataSourceAdapter` 基类，使用 `aiomysql` 实现同步/异步查询。
必须使用参数化查询（`%s`），复用 `ClickHouseAdapter` 的逻辑结构：
- `_build_where`: 生成带有 `%s` 的 SQL。
- `execute`: 执行并返回 `ResultSet`。

### 3. Data Source Selection in Metadata
资源元数据中的 `data_source` 字段将存储 `sys_data_source.name` 或 `id`。前端提供下拉框拉取所有可用数据源。

## Risks
- **资源泄露**: 动态创建连接池如果不及时关闭可能导致连接溢出。
- **方案**: 数据源删除或修改连接信息时，必须销毁旧的旧池。
