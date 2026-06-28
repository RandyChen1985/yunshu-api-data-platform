## 1. Database & Models

- [x] 1.1 创建 `db-prod/V19-implement_semantic_metadata.sql`，定义 5 张核心元数据表及级联删除约束。
- [x] 1.2 编写 SQL 验证脚本，确保 DDL 在本地 MySQL 中正确执行。

## 2. Backend Implementation (Services & APIs)

- [x] 2.1 实现 `MetadataService`：支持 Dataset, Table, Column 的基础 CRUD。
- [x] 2.2 实现 `MetadataGeneratorService`：复刻 AI 解析 DDL 的逻辑及 Prompt 模板。
- [x] 2.3 实现 `MetadataYamlService`：实现元数据到 YAML 的序列化转换逻辑。
- [x] 2.4 实现 `MetadataSimulatorService`：实现轻量级的模拟检索逻辑。
- [x] 2.5 注册 API 路由：在 `app/api/portal/endpoints/meta_v2.py` 中挂载所有端点。

## 3. Frontend Implementation (Views & Components)

- [x] 3.1 增加导航：在主侧边栏增加“元数据中心”入口。
- [x] 3.2 实现 `MetadataDatasets.vue`：数据集卡片展示、状态切换、删除逻辑。
- [x] 3.3 实现 `SmartImportWizard.vue`：复刻带进度条的 DDL 导入向导。
- [x] 3.4 实现 `MetadataTables.vue`：多选项卡详情页（Table, Metric, Relationship, Visual）。
- [x] 3.5 实现 `SearchSimulator.vue`：独立的检索模拟器页面。

## 4. Testing & Verification

- [x] 4.1 编写单元测试：验证 DDL 智能解析的 JSON 准确性。
- [x] 4.2 联调测试：从 DDL 导入到生成 YAML 的全链路打通。
- [x] 4.3 演示验证：模拟用户提问并展示召回的 YAML 效果。
