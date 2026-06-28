## ADDED Requirements
### Requirement: 数据源管理模块 (Data Source Management)
系统必须 (SHALL) 提供数据源管理模块，允许管理员维护外部数据库的连接参数。

#### Scenario: 仅管理员访问
- **WHEN** 用户角色为 `admin`
- **THEN** 在侧边栏显示“数据源管理”菜单。
- **WHEN** 用户角色为 `user`
- **THEN** 隐藏“数据源管理”菜单，且直接访问 API 时返回 403 Forbidden。

#### Scenario: 连通性测试
- **WHEN** 编辑数据源时点击“测试连接”
- **THEN** 系统尝试建立真实连接并返回结果。

### Requirement: 元数据与数据源关联 (Meta-Data Linking)
在创建或编辑资源元数据时，必须 (MUST) 通过下拉选择器关联已定义的数据源。

#### Scenario: 动态数据源列表
- **WHEN** 打开资源编辑页面
- **THEN** “数据源”选项由后端接口动态加载。
