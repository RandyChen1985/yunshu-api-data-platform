# ccg-schema Specification

## Purpose
TBD - created by archiving change enhance-ccg-schemas. Update Purpose after archive.
## Requirements
### Requirement: CCG API Schemas
The CCG (Cloud Management) placeholder APIs MUST provide strict Pydantic response models in the OpenAPI documentation.

#### Scenario: Schema Availability
- **WHEN** 查看 CCG 相关接口文档。
- **THEN** 必须能看到明确的 Response Body 结构，而不是 "Any" 或空。

#### Scenario: Realistic Examples
- **WHEN** 查看 Schema 示例。
- **THEN** 示例值应反映真实的云管资源属性（如 IP 地址、CPU核数等）。

