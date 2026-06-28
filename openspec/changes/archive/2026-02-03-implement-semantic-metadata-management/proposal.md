## Why
目前 SQL 实验室生成的 SQL 准确率受限于基础 Schema 信息（仅表名和字段名），AI 无法理解字段的业务含义或枚举逻辑。通过复刻 `ai-agent-platform` 的语义化元数据管理系统，我们可以为 AI 提供深度的业务语境（术语、同义词、枚举、指标逻辑和关联关系），从而将 Text2SQL 转化为真正的“语义化取数”。

## What Changes
- **后端模型构建**：在本项目中复刻 `meta_datasets`, `meta_tables`, `meta_columns`, `meta_metrics`, `meta_relationships` 的数据库结构。
- **元数据管理接口**：实现完整的元数据 CRUD 接口，并复刻“智能 DDL 解析导入”逻辑。
- **管理 UI 开发**：
  - 数据集（Dataset）概览与卡片管理。
  - 数据表与字段详情配置，支持枚举值和同义词编辑。
  - 业务指标（Metric）与表关联关系（Relationship）配置。
- **YAML 引擎**：实现将复杂的元数据结构自动转化为专为 LLM 优化的 YAML 片段。
- **检索模拟器 (Simulation)**：开发专门的“检索测试”页面，模拟 AI Agent 的检索过程，验证关键词召回准确性并预览生成的 Prompt 上下文。

## Capabilities

### New Capabilities
- `semantic-metadata`: 提供元数据的存储、结构化管理、智能 DDL 解析、YAML 生成以及检索效果模拟。

### Modified Capabilities
- `lab-ai-generation`: 调整现有的 SQL 生成逻辑，预留接入语义化上下文的接口（当前阶段先实现管理和模拟，暂不强制干扰现有生成逻辑）。

## Impact
- **Database**: 新增 5 张 `meta_` 核心表。
- **Frontend**: 在管理后台增加“元数据中心”导航，开发 2 个主页面及多个复杂的配置 Modal。
- **Backend API**: 新增以 `/api/portal/meta/v2` 为前缀的系列管理接口。
- **AI Integration**: 增加 `metadata-specialist` 智能体角色定义，用于 DDL 解析。
