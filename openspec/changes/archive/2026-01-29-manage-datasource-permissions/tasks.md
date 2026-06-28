## 1. 后端实现
- [x] 1.1 更新 `app/services/permission_service.py`，支持 `datasource` 和 `data_table` 权限类型。
- [x] 1.2 更新 `app/schemas/auth.py`，增加权限字段。
- [x] 1.3 更新 `app/api/v1/endpoints/sql_execution.py`，实现 SQL 表名提取和权限校验逻辑。
- [x] 1.4 新增 API `GET /api/portal/meta/datasources/{id}/tables`，用于前端获取表列表（复用 Introspection Service）。
- [x] 1.5 更新角色管理 API (`app/api/portal/management.py`)，支持接收和保存 `datasources` 和 `data_tables` 权限列表。

## 2. 前端实现
- [x] 2.1 修改 `frontend/src/views/Roles.vue`，增加“数据资产” (Data Assets) 子标签页。
- [x] 2.2 实现数据源列表的获取与展示。
- [x] 2.3 实现“点击加载表列表”的交互组件（支持多选）。
- [x] 2.4 更新保存逻辑，将选中的数据源和表权限提交给后端。

## 3. 测试
- [x] 3.1 单元测试：`PermissionService` 的新逻辑。
- [x] 3.2 集成测试：SQL 执行接口的权限拦截。
- [x] 3.3 界面测试：确保权限能正确保存并回显。
