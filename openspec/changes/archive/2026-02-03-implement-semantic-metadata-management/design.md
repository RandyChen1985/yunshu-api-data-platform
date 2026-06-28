## Context
目前的 SQL 实验室主要依赖于数据库的基础 Schema 信息（表名和列名）。为了提升 AI 生成 SQL 的合规性和准确率，我们需要引入一套“业务语义层”。通过复刻 `ai-agent-platform` 的成熟设计，我们可以让 AI 理解物理字段背后的业务逻辑、枚举含义、计算口径以及表间关联路径。

## Goals / Non-Goals

**Goals:**
- **数据结构复刻**：在本项目数据库中建立一套完整的语义元数据存储体系（Dataset, Table, Column, Metric, Relation）。
- **智能导入能力**：复刻基于 LLM 的 DDL/自然语言元数据解析导入逻辑。
- **配置管理 UI**：提供直观的界面来维护字段的术语（Term）、枚举值（Enums）和同义词（Synonyms）。
- **语义召回模拟**：实现一个检索测试页面，验证关键词到元数据的召回效果。
- **YAML 导出引擎**：实现将复杂的元数据关系转化为专为 LLM 优化的 YAML 上下文片段。

**Non-Goals:**
- **RAGFlow 物理同步**：暂不实现与外部 RAGFlow 系统的物理同步（本阶段仅验证语义管理和本地生成的 YAML 上下文）。
- **Agent 复杂编排**：本次变更仅关注“元数据知识库”的建设，暂不涉及多 Agent 的复杂协作。

## Decisions

### 1. 数据库存储：原生 SQL + Repository 封装
- **决策**：不引入 SQLAlchemy 或其他全功能 ORM。在 `db-prod/` 下编写原生 DDL 迁移文件。
- **理由**：保持本项目现有的轻量级数据库访问模式。但在 `app/services` 层通过 Python 类对 SQL 操作进行封装，模拟 ORM 的易用性，降低 CRUD 代码的复杂度。

### 2. UI 架构：深度适配版搬运
- **决策**：搬运 `ai-agent-platform` 的 Vue 3 组件逻辑，但外观使用本项目现有的 Tailwind CSS 变量和组件风格重绘。
- **理由**：技术栈（Vue3/Tailwind/Heroicons）完全一致，复用逻辑可以节省大量开发时间，同时重绘外观能保证系统的统一性。

### 3. AI 逻辑：独立 Service 化
- **决策**：创建 `MetadataGeneratorService`，复刻原有的 `metadata-specialist` 提示词模板和 `JsonOutputParser`。
- **理由**：该逻辑已被验证在 Text2SQL 领域非常有效，能够自动推断出高质量的业务术语。

### 4. 检索模拟方案：内存式计算 + YAML 预览
- **决策**：由于暂不接入 RAGFlow，模拟搜索将采用基础的关键词权重或轻量级的局部向量匹配，重点展示生成的 YAML 片段是否准确。

## Risks / Trade-offs

- **[Risk] 性能瓶颈** → **[Mitigation]** 元数据量级通常在万级以内，查询时将引入 Redis 缓存机制，避免频繁的物理表 JOIN。
- **[Trade-off] 原生 SQL 维护成本** → 为了不破坏项目纯净度，放弃 ORM 意味着需要手写更多 SQL。我们将通过详细的 Repository 单元测试来保证正确性。

## Migration Plan
1. **DB**: 执行 `V19-implement_semantic_metadata.sql`。
2. **Backend**: 增加管理 API。
3. **Frontend**: 增加“元数据中心”导航和相关管理视图。
4. **Verification**: 通过“检索模拟器”验证 YAML 生成逻辑。
