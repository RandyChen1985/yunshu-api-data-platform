## ADDED Requirements

### Requirement: Intelligent Context Retrieval
SQLLab 的 AI 助手必须能够根据用户的自然语言输入自动检索并注入相关的元数据上下文。

#### Scenario: Automatic recall when no tables selected
- **WHEN** 用户在未勾选任何表的情况下提交 AI 生成请求
- **AND** 系统开启了“智能关联”模式
- **THEN** 系统必须基于用户的 Prompt 调用向量检索引擎
- **AND** 将召回的 Top-K 语义片段注入 AI 上下文

### Requirement: Hybrid Metadata Source
上下文生成逻辑必须优先使用语义库中的信息，并在缺失时优雅回退到物理结构。

#### Scenario: Preference for semantic terms
- **WHEN** 系统为某张表生成上下文
- **IF** 该表在 `meta_v2` 中有定义
- **THEN** 生成的 YAML 必须包含业务术语、枚举定义和关联关系
- **ELSE** 生成基于原始数据库 Schema 的基础 YAML
