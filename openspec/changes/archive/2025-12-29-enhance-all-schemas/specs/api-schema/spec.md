## ADDED Requirements

### Requirement: Comprehensive API Schemas
The system MUST provide detailed Pydantic schemas with examples for all public API endpoints.

#### Scenario: Rich Response Examples
- **WHEN** 开发者或 AI Agent 查看 OpenAPI 文档中的 Model 定义。
- **THEN** 每一个字段都必须包含 `description` 和 `example`。
- **AND** `example` 值必须符合字段的实际数据类型和业务格式（如时间格式、ID格式）。

#### Scenario: Self-Descriptive Fields
- **WHEN** 查看字段描述。
- **THEN** 描述应清晰阐述字段的业务含义，而不仅仅是字段名的翻译。
