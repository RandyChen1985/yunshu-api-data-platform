## 上下文
现有的 `sys_ui_permissions` 表结构非常灵活，支持 `perm_type` 和 `perm_code`。我们将复用这一结构来存储数据源和数据表权限。

## 目标
- 复用现有的 RBAC 存储机制 (`sys_ui_permissions`)。
- 支持**角色**和**用户**两个维度的权限合并。
- 实现**数据源级**和**表级**的级联控制，遵循**显式授权**原则。

## 技术决策
- **权限类型 (Permission Types)**：
    - `datasource`：编码格式为 `ds:{source_name}`。
    - `data_table`：编码格式为 `ds:{source_name}:table:{table_name}`。
    - **全通标识**：`ds:{source_name}:table:*` (代表该数据源下所有表)。

- **校验逻辑 (关键变更)**：
    1. **全局校验**：用户必须拥有 `system.sql.execute` 权限。
    2. **数据源校验**：必须拥有 `ds:{source_name}`。
    3. **数据表校验**：
        - 步骤 A：检查用户/角色是否拥有 `ds:{source_name}:table:*`。如果有，**直接放行**。
        - 步骤 B：如果无通配符权限，则检查用户是否拥有 SQL 中引用的**每一张**具体表的权限 `ds:{source_name}:table:{table_name}`。
        - 步骤 C：如果既无通配符，又缺少具体表权限（或配置列表为空），则**拒绝访问**。

- **前端交互设计**：
    - 在表选择器中，增加一个**“所有表 (ALL)”**的特殊选项。
    - 勾选“所有表”时，前端提交 `ds:{name}:table:*`。
    - 否则，提交具体选中的表列表。

- **新增 API**：
    - `GET /api/portal/meta/datasources/{id}/tables`: 返回 `{ schema: string, table: string }[]`。
    - `PUT /api/portal/management/roles/{id}/permissions`: 扩展 Request Body。

## 风险与权衡
- **SQL 解析**：依赖 `sqlparse` 提取表名。
- **配置繁琐度**：相比之前的“不配即全通”，现在管理员必须为每个数据源至少配置一个表或显式选“所有表”，否则用户无法使用。但这换来了更高的安全性。

## 待定问题
- 暂无。
