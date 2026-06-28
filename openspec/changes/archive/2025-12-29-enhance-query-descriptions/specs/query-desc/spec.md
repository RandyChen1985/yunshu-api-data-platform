## ADDED Requirements

### Requirement: Descriptive Query Parameters
All explicit API query parameters MUST have detailed Chinese descriptions and realistic examples in the OpenAPI documentation.

#### Scenario: Self-Documenting Filters
- **WHEN** 查看资源列表接口（如 `/yunshu/rooms`）。
- **THEN** 每一个 Query 参数（如 `jfbm`）都必须说明其业务含义（如“机房编码”）。
- **AND** 必须提供 `examples` 字段。
