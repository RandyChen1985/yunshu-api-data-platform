# api-schema Specification

## Purpose
TBD - created by archiving change enhance-all-schemas. Update Purpose after archive.
## Requirements
### Requirement: Comprehensive API Schemas
The system MUST provide detailed Pydantic schemas with examples for all public API endpoints.

#### Scenario: Rich Response Examples
- **WHEN** 开发者或 AI Agent 查看 OpenAPI 文档中的 Model 定义。
- **THEN** 每一个字段都必须包含 `description` 和 `example`。
- **AND** `example` 值必须符合字段的实际数据类型和业务格式（如时间格式、ID格式）。

#### Scenario: Self-Descriptive Fields
- **WHEN** 查看字段描述。
- **THEN** 描述应清晰阐述字段的业务含义，而不仅仅是字段名的翻译。

### Requirement: 全局流控检查 (Global Rate Limiting)
系统必须对所有 /api/v1 接口执行基于 Redis 的流控检查。系统应在响应头中返回限流状态信息。

#### Scenario: 正常请求
- **Given** 用户持有有效的 API Key
- **And** 用户当前的请求频率未达到所属角色的上限
- **When** 用户发起 API 调用
- **Then** 系统应正常返回业务数据
- **And** 响应头必须包含 `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

#### Scenario: 超限拦截
- **Given** 用户当前的请求频率已达到上限
- **When** 用户再次发起调用
- **Then** 系统必须返回 HTTP 429 Too Many Requests 状态码
- **And** 响应头仍应包含限流状态信息，且包含详细的错误信息

