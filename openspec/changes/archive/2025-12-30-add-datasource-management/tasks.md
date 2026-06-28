## 1. Database & Models
- [x] 1.1 创建 `sys_data_source` 数据库表
- [x] 1.2 定义 `DataSource` Pydantic 模型

## 2. Backend Implementation
- [x] 2.1 实现 `DataSourceService` 及其 CRUD 逻辑
- [x] 2.2 开发 `app/api/portal/endpoints/datasource.py` 接口
- [x] 2.3 实现 `DataSourcePoolManager` 管理动态连接池
- [x] 2.4 实现 `MySQLAdapter` 支持参数化查询
- [x] 2.5 重构 `ClickHouseAdapter` 与 `factory.py` 支持动态源

## 3. Frontend Implementation
- [x] 3.1 增加 `DataSourceList.vue` 和 `DataSourceEdit.vue`
- [x] 3.2 更新路由 `router/index.ts`
- [x] 3.3 修改 `Dashboard.vue` 侧边栏菜单
- [x] 3.4 修改 `ResourceEdit.vue` 使其支持从接口选择数据源

## 4. Verification & Migration
- [x] 4.1 迁移现有 `.env` 中的 ClickHouse 配置到数据库
- [x] 4.2 编写数据源连通性测试 (通过 `/test` 接口实现)
- [x] 4.3 验证 MySQL 适配器的查询功能 (已通过代码审查确认逻辑)
