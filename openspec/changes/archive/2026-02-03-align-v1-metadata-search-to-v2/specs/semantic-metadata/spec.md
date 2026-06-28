## MODIFIED Requirements

### Requirement: Search Simulator (检索模拟)
系统必须提供支持多策略的元数据检索能力，包括关键词匹配和语义向量搜索。

#### Scenario: V1 语义搜索对齐
- **WHEN** 外部系统调用 V1 `/search` 接口且 `search_type="semantic"`
- **THEN** 系统必须调用向量库进行 HNSW 召回，并根据 `enable_rerank` 参数执行可选的重排序
- **AND** 返回的 YAML 上下文必须仅包含命中的原子对象片段
- **AND** 响应中不应包含任何内部调试日志 (`debug_logs`)
