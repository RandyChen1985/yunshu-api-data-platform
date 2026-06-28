<!--
Spec: openspec/changes/manage-dynamic-resource-configs/specs/dynamic_resource_config/spec.md
Design: openspec/changes/manage-dynamic-resource-configs/design.md
Proposal: openspec/changes/manage-dynamic-resource-configs/proposal.md
-->

# 任务：动态资源配置管理

- [x] **数据库 Schema**
    - [x] 创建 `V1-dynamic_resource_config.sql`，包含 `sys_resource_meta` 表结构和初始数据。
    - [x] 定义 `ResourceConfig` 的 SQLAlchemy/Pydantic 模型。
    - [x] (可选) 验证 SQL 执行。

- [x] **Meta Service (元数据服务)**
    - [x] 在 `app/services/meta_service.py` 中实现 `MetaService` 类。
    - [x] 实现带缓存的 `get_config(key)` 方法（使用 `lru_cache` 或手动字典缓存）。
    - [x] 实现 `refresh_config()` 刷新方法。

- [x] **API Endpoints (接口)**
    - [x] 创建 `app/api/portal/endpoints/meta.py`。
    - [x] 实现 `GET /` 列表查询接口。
    - [x] 实现 `POST /` 创建接口。
    - [x] 实现 `PUT /{key}` 更新接口。
    - [x] 实现 `DELETE /{key}` 删除接口。
    - [x] **增强**: 在 Create/Delete 逻辑中调用 `AuthService` 同步更新权限表 (`sys_permissions` 或对应逻辑)。
    - [x] 在 `app/main.py` 中注册新路由。

- [x] **Universal Data API (通用数据接口)**
    - [x] 创建 `app/api/v1/endpoints/universal.py`。
    - [x] 实现 `GET /api/v1/resources/{resource_key}` 接口。
    - [x] 实现动态参数解析逻辑 (将 Query Params 转换为 LogicalQuery filters)。
    - [x] 注册路由到 `app/api/v1/api.py`。
    - [x] **Docs**: 重写 `app.openapi` 逻辑，遍历 `MetaService` 动态注入每个资源的 Path 定义到 OpenAPI Schema。

- [x] **Refactor Data Adapter (重构数据适配器)**
    - [x] 修改 `app/services/data_adapter/factory.py`，支持基于配置的动态适配器实例化。
    - [x] 确保 `ClickHouseAdapter` 仅作为 `clickhouse` 类型的实现。
    - [x] 验证架构设计是否容易扩展支持 `mysql` 或其他类型。

- [x] **Frontend Development (前端开发)**
    - [x] 创建 `src/views/resources/ResourceList.vue` (资源列表)。
    - [x] 创建 `src/views/resources/ResourceEdit.vue` (资源编辑/新建)。
    - [x] 实现动态表单逻辑：根据 `Data Source` 切换配置字段。
    - [x] **UX**: 添加 Tooltips、HelpText 和 Placeholders，特别是针对 SQL 模式的示例说明。
    - [x] **Test Console**: 开发侧边栏测试面板，支持动态生成筛选表单，并展示查询结果/SQL。
    - [x] 集成 "Test Query" 按钮，调用后端 API 验证配置。
    - [x] 更新路由配置 `src/router/index.ts`。

- [x] **Data Migration (数据迁移)**
    - [x] 创建脚本或启动钩子 (Startup Hook)，将现有的 5 个资源配置（`yunshu_rooms` 等）作为种子数据写入新表。

- [x] **Testing (测试)**
    - [x] `MetaService` 的单元测试。
    - [x] Meta API 的集成测试。
    - [x] 使用新动态配置的 `ClickHouseAdapter` 回归测试。