# Change: 数据源管理与动态适配器支持 (Data Source Management & Dynamic Adapter Support)

## Why
目前系统的数据源（ClickHouse）配置硬编码在环境变量中，且元数据管理（Metadata Management）无法灵活切换不同的物理数据库实例。为了支持多租户、多环境以及多类型数据库（MySQL, Oracle等），需要引入动态数据源管理功能，并实现 MySQL 适配器。

## What Changes
- **后端 (Backend)**:
    - 新增 `sys_data_source` 表，存储连接信息（Host, Port, User, Password, Type）。
    - 提供数据源 CRUD 接口（仅管理员可用）。
    - 重构 `ClickHouseAdapter`，使其根据数据源 ID 动态获取连接池。
    - 实现 `MySQLAdapter` 并注册到工厂方法。
    - 实现 `DataSourcePoolManager`，管理不同数据源的连接池生命周期。
- **前端 (Frontend)**:
    - 侧边栏新增“数据源管理”菜单，放置在“元数据管理”之前。
    - 开发数据源列表页、新增/编辑弹窗。
    - 修改元数据编辑页面，将“数据源”由输入框改为下拉选择器。

## Impact
- Affected specs: `adapter`, `admin-mgt`
- Affected code: 
    - `app/services/data_adapter/*`
    - `app/services/meta_service.py`
    - `app/core/database.py`
    - `frontend/src/views/Dashboard.vue`
    - `frontend/src/router/index.ts`
