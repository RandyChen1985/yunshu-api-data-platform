# Change: Enhance CCG Schemas

## Why
`app/api/v1/endpoints/ccg.py` 中的接口目前 `response_model=None`，导致 OpenAPI 文档中缺乏对云管资源数据的结构描述。这对希望对接云管数据的 AI Agent 是一个阻碍，即使目前是占位符数据，也应该提供明确的 Schema。

## What Changes
- **ADDED**: `app/api/v1/schemas/ccg.py` 定义 CCG 相关的 Pydantic 模型（Resource, VM, Container）。
- **MODIFIED**: `app/api/v1/endpoints/ccg.py` 引入这些模型作为 `response_model`。

## Impact
- **影响范围**: CCG 云管接口的 OpenAPI 文档。
- **风险**: 低。
