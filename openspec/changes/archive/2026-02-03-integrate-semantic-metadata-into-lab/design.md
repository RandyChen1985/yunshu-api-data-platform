## Context

目前 SQL 实验室的 AI 功能依赖于 `MetaService.get_schema_context` 获取物理表结构。这种方式虽然准确，但缺乏业务语义，且要求用户必须手动勾选表，导致操作繁琐且易出错（用户可能漏选关联表）。

## Goals / Non-Goals

**Goals:**
- 实现从“物理元数据”到“语义元数据”的无缝切换。
- 引入“自动召回”机制，降低用户手动选表的成本。
- 提升 AI 对复杂业务指标和表关联的理解能力。

**Non-Goals:**
- 不改变物理元数据抓取作为底层的保底方案。
- 不影响 SQLLab 现有的 SQL 运行逻辑。

## Decisions

### 1. 统一接口，按需路由
**决策**：扩展 `get_schema_context(source_id, tables, prompt)` 的入参。
**理由**：在保留原有参数的基础上增加 `prompt`，使得后端可以根据参数组合自动判断是执行“指定表提取”还是“全域语义检索”。

### 2. 混合元数据提取逻辑
**逻辑顺序**：
1.  **Semantic Check**: 尝试在 `meta_v2` 库中通过物理表名查找。
2.  **YAML Generation**: 如果找到，调用 `MetadataYamlService.generate_table_yaml`。
3.  **Physical Fallback**: 如果语义库中不存在该表，则调用原有的数据库适配器抓取物理结构并格式化为 YAML。
4.  **Enrichment**: 自动注入相关的 `metrics` 和 `relationships`。

### 3. 前端“智能上下文”开关
**决策**：在侧边栏顶部增加“智能关联上下文”开关。
**理由**：
- **开启**：AI 生成请求时不强制校验 `tables` 列表，后端根据 `prompt` 自动搜索。
- **关闭**：维持现有逻辑，仅针对勾选的表生成 SQL。

## Risks / Trade-offs

- **[Risk] 召回不准**：向量召回可能漏掉某些表或引入无关表。
  - **Mitigation**: 在 AI 响应中明确标识“已自动关联的表”，并允许用户通过手动勾选覆盖。
- **[Risk] Token 溢出**：丰富的语义信息会导致 Prompt 变长。
  - **Mitigation**: 严格限制语义召回的 Top-K 数量（建议 3-5 个片段）。
