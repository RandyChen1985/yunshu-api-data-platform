## Why

目前 SQL 实验室 (SQLLab) 的 AI 辅助功能（生成、修改、纠错）仅依赖于实时的物理表结构扫描。由于物理结构缺乏业务术语映射、复杂的指标计算逻辑以及跨表关联指南，AI 在处理业务化查询时准确率较低。

通过接入已建立的语义化元数据系统，我们可以为 AI 提供更具“业务深度”的上下文，并消除用户必须手动勾选表的繁琐操作。

## What Changes

- **核心逻辑重构**：修改 `MetaService.get_schema_context`，使其能够从 `meta_v2` 语义库中获取原子化 YAML 片段，而不是原始的 `SHOW COLUMNS` 结果。
- **自动语义召回**：在执行 AI 任务前，若未指定上下文表，系统将基于用户的自然语言描述调用语义检索引擎（含向量召回与 Rerank）自动锁定相关资产。
- **UI 交互增强**：
    - 在 SQLLab AI 助手界面增加“自动关联元数据”模式。
    - 允许用户在“手动勾选表”和“全域语义搜索”之间自由切换或结合使用。
- **上下文内容丰富化**：注入的上下文将自动包含相关的 `meta_metrics`（指标定义）和 `meta_relationships`（关联路径），极大提升多表联查的成功率。

## Capabilities

### New Capabilities
- `lab-semantic-integration`: 定义 SQLLab 与语义元数据层的集成规范。

### Modified Capabilities
- `semantic-metadata`: 扩展元数据检索接口，以更好地服务于 SQL 生成场景（例如：针对 Text2SQL 的专用组装策略）。

## Impact

- `app/services/meta_service.py`: 需重写 `get_schema_context` 方法。
- `app/api/portal/endpoints/lab.py`: 需调整 AI 请求参数，支持透传用户 Prompt 用于语义搜索。
- `frontend/src/views/SQLLab.vue`: UI 调整，增加上下文模式切换。
