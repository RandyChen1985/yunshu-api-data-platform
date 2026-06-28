# 功能：动态资源配置管理

## ADDED Requirements

### Requirement: 资源元数据存储 (Resource Metadata Storage)
系统**必须 (MUST)** 将资源配置元数据存储在持久化数据库 (`sys_resource_meta`) 中，并支持多数据源类型的配置。

#### Scenario: 多数据源配置支持
- **Given** 管理员定义了一个新资源 "user_stats"
- **And** 选择数据源类型为 "mysql"
- **When** 配置保存后
- **Then** 系统应能识别该类型并使用 MySQL 适配器进行数据查询。
- **And** `sys_resource_meta` 中应记录 `data_source=mysql`。

### Requirement: 自定义 SQL 模式 (Child-Resource / SQL Mode)
系统**必须 (MUST)** 支持通过自定义 SQL 定义资源的数据集，以支持复杂的预聚合或多表关联需求。

#### Scenario: 基于复杂查询的资源
- **Given** 管理员需要发布一个 "复杂统计报表" 资源，涉及多张表的 JOIN 和 GROUP BY
- **When** 在资源配置中选择模式为 `SQL`
- **And** 输入 SQL: `SELECT a.id, count(b.id) as num FROM table_a a JOIN table_b b ON a.id=b.aid GROUP BY a.id`
- **Then** 系统应能正确保存
- **And** 通过 API 查询该资源时，系统自动将该 SQL 作为子查询执行：`SELECT * FROM (...) WHERE ... LIMIT ...`

### Requirement: 通用 RESTful 接口 (Universal RESTful API)
系统**必须 (MUST)** 提供通用的 RESTful 接口路径，以支持对动态资源的即时访问。

#### Scenario: 动态路由
- **Given** 管理员配置了一个新资源 `key="audit_logs"`
- **When** 客户端立即发起请求 `GET /api/v1/resources/audit_logs?user_id=123`
- **Then** 系统应成功路由该请求
- **And** 返回 `audit_logs` 表中过滤后的数据
- **And** 此过程**不需要**重启服务或部署新代码。

### Requirement: 动态 API 文档 (Dynamic API Documentation)
系统**必须 (MUST)** 能够根据配置的资源动态刷新 API 文档。

#### Scenario: API 文档自动生成
- **Given** 系统中存在资源 `yunshu_rooms` 和 `audit_logs`
- **When** 开发者访问 `/docs` (Swagger UI)
- **Then** 文档中应分别独立列出 `GET /api/v1/resources/yunshu_rooms` 和 `GET /api/v1/resources/audit_logs` 两个接口
- **And** 接口参数应包含各自配置的过滤字段（如 `yunshu_rooms` 显示 `jfbm` 参数，`audit_logs` 显示 `user_id` 参数）
- **And** 接口应根据 `resource_group` 字段进行折叠分组（例如 "云枢业务", "系统审计"）。

### Requirement: 资源分组 (Resource Grouping)
系统**必须 (MUST)** 支持对资源进行分组定义，以优化文档 and 权限管理的展示。

#### Scenario: 权限选择分组
- **Given** 管理员在角色管理页面为 "Operator" 分配权限
- **When** 页面加载权限列表时
- **Then** 资源类的权限应按照配置的 `resource_group` 进行归类显示（例如 "动环监控" 组下包含 5 个指标资源），而不是散乱排列。

### Requirement: 可视化配置 UI (Visual Configuration UI)
系统**必须 (MUST)** 提供友好的可视化编辑界面。

#### Scenario: 可视化表格编辑
- **Given** 管理员正在编辑 "yunshu_rooms" 的字段配置
- **When** 他需要添加一个新字段 `cpu_count`
- **Then** 他可以在 UI 的表格中点击“添加行”，输入字段名，而不是手动编辑 JSON 字符串。

#### Scenario: 辅助自动填充
- **Given** 管理员输入了物理表名 `ck_fact_yunshu_resroom_hbase`
- **When** 点击“获取表结构”按钮
- **Then** 前端应自动列出该表的所有列，允许用户一键勾选将其加入到 API 返回字段中。

#### Scenario: 操作引导提示
- **Given** 管理员切换到 `SQL` 模式
- **Then** 界面应立即展示 Tooltip 或 Alert 提示用户：“自定义 SQL 将被作为子查询运行，请确保 SQL 语法独立可执行且不含分号。”
- **And** 输入框中应预置示例代码（Placeholder）以展示期望的格式。

#### Scenario: 带参测试预览
- **Given** 管理员配置了筛选字段 `["status", "city"]`
- **When** 点击侧边栏的“测试”面板
- **Then** 界面应显示 `status` 和 `city` 的输入框
- **When** 管理员输入 `status=active` 并点击运行
- **Then** 系统应返回经过过滤的真实数据预览
- **And** (可选) 展示后端生成的 SQL 语句供核对。

### Requirement: 安全权限 (Security)
资源配置管理接口**必须 (MUST)** 仅允许拥有管理员权限的用户访问。

#### Scenario: 非管理员禁止访问
- **Given** 一个拥有普通用户权限的 Token
- **When** 尝试请求 `POST /api/portal/meta/resources`
- **Then** 系统应拒绝请求并返回 `403 Forbidden`。

### Requirement: 权限自动绑定 (Automatic Permission Binding)
系统**必须 (MUST)** 在创建新资源时自动初始化权限控制项。

#### Scenario: 创建资源时同步权限
- **Given** 管理员创建了新资源 `key="audit_logs"`
- **When** 资源创建成功
- **Then** 系统应在权限管理模块中自动注册一个名为 `audit_logs` 的权限项
- **And** 默认赋予 `Admin` 角色对该资源的访问权
- **And** 其他角色（如普通用户）默认无权访问，需手动授权。

### Requirement: 运行时动态加载 (Runtime Dynamic Loading)
数据适配器 (Data Adapter) **必须 (MUST)** 在运行时从元数据服务动态加载资源配置。

#### Scenario: 使用动态配置执行查询
- **Given** 收到一个 `GET /api/v1/resources/virtual_machines` 的请求
- **When** 适配器处理该查询时
- **Then** 它应从 Meta Service 获取 "virtual_machines" 的最新配置（表名、字段等）
- **And** 使用 these 动态属性构建 SQL 查询语句。

### Requirement: 配置缓存 (Configuration Caching)
系统**必须 (MUST)** 实现缓存机制：首次读取时从数据库加载并缓存（Lazy Load），后台修改配置时立即刷新/失效缓存。

#### Scenario: 首次读取写入缓存 (Lazy Loading)
- **Given** 系统刚启动，缓存为空
- **When** 收到第一个针对 "yunshu_rooms" 的查询请求
- **Then** 系统从数据库查询该配置
- **And** 将配置存入内存缓存
- **And** 后续相同请求直接从缓存读取，不产生数据库查询。

#### Scenario: 修改配置触发失效 (Write-Invalidate)
- **Given** "yunshu_rooms" 的配置已缓存在内存中
- **When** 管理员通过后台 API 修改了该配置（例如增加了字段）
- **Then** 系统应立即清除 "yunshu_rooms" 的内存缓存
- **And** 下一次查询请求应重新从数据库加载最新配置。

## MODIFIED Requirements
*无*

## REMOVED Requirements
- **Requirement: 硬编码配置**
    - `ClickHouseAdapter` 中的 `RESOURCE_CONFIGS` 字典**必须 (MUST)** 被移除，或替换为动态加载机制。
