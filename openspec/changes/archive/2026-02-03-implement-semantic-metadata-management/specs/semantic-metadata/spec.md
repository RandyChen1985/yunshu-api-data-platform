# Semantic Metadata Specification

## Overview
语义化元数据系统是连接物理数据库与 AI 逻辑的桥梁。它通过维护表、列、指标、关系这四个维度的业务信息，为 Text2SQL 提供高质量的 Prompt 上下文。

## Data Model (Metadata Core)

### 1. Dataset (数据集/业务域)
- **ID**: 唯一标识。
- **name**: 物理编码 (如 `ops_metrics`)。
- **display_name**: 业务名称 (如 `运维监控数据集`)。
- **data_source**: 关联的数据源 ID (如 `default_clickhouse`)。
- **status**: 启用/禁用状态。

### 2. Table (数据表)
- **physical_name**: 数据库中的真实表名。
- **term**: 业务术语 (如 `机房表`)。
- **description**: 表用途描述。
- **synonyms**: 同义词列表 (JSON 数组，如 `["数据中心", "IDC"]`)。

### 3. Column (数据字段)
- **physical_name**: 真实字段名。
- **term**: 业务术语 (如 `PUE值`)。
- **type**: 数据类型 (String, Float, Int 等)。
- **enums**: 枚举映射 (JSON 数组，如 `[{"value": 1, "label": "正常"}]`)。
- **synonyms**: 字段级同义词。
- **examples**: 典型值示例 (用于 LLM Few-shot)。

### 4. Metric (业务指标)
- **name**: 指标物理编码。
- **display_name**: 指标名称 (如 `PUE均值`)。
- **calculation_logic**: SQL 计算逻辑 (如 `avg(pue)`)。
- **unit**: 单位。

### 5. Relationship (实体关系)
- **source_table_id / target_table_id**: 关联的两个表。
- **join_condition**: Join 表达式 (如 `t1.room_id = t2.id`)。
- **join_type**: LEFT, INNER 等。

## Functionality

### 1. Smart Import (智能导入)
- **Input**: 接收 SQL DDL、Markdown 表格或自然语言描述。
- **AI Task**: 调用 `metadata-specialist` 智能体，分析输入内容并自动推断所有 `term`、`enums` 和 `synonyms`。
- **Output**: 返回结构化的 JSON 结果供用户预览和微调。

### 2. YAML Generation (YAML 生成引擎)
- **Rule**: 将整个数据集序列化为精简的 YAML 格式。
- **Context Injection**: 
  - 表与列按物理-业务对照排列。
  - 必须包含枚举值说明。
  - 必须注入相关的 Relationship 信息作为“辅助 Join 指南”。

### 3. Search Simulation (检索模拟)
- **Workflow**:
  1. 用户输入自然语言问题。
  2. 系统模拟关键词提取。
  3. 召回相关的 Table/Metric。
  4. 渲染生成的 YAML 片段。
  5. 允许管理员评估召回结果的准确度。

## API Endpoints
- `GET /api/portal/meta/v2/datasets`: 列表查询。
- `POST /api/portal/meta/v2/datasets/import`: 智能 DDL 分析。
- `POST /api/portal/meta/v2/datasets/{id}/sync`: 保存并确认元数据。
- `GET /api/portal/meta/v2/datasets/{id}/yaml`: 获取 AI YAML。
- `POST /api/portal/meta/v2/simulator/retrieve`: 执行模拟检索。
