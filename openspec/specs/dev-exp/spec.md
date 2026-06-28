# dev-exp Specification

## Purpose
TBD - created by archiving change improve-developer-experience. Update Purpose after archive.
## Requirements
### Requirement: Enhanced API Documentation
The system MUST provide highly readable and debuggable API documentation.

#### Scenario: Persistent Authorization in Swagger
- **WHEN** 访问 `/docs` 路径并输入 API Key。
- **THEN** 刷新页面后，API Key 应该被保留在 Authorize 状态中。

#### Scenario: Detailed Query Schema
- **WHEN** 在文档中查看 `/query` 接口。
- **THEN** 开发者应该能看到 `filters` 参数的详细结构定义和示例。

### Requirement: Developer Onboarding Assets
The system MUST provide onboarding guides and example code to accelerate developer integration.

#### Scenario: Onboarding Guide
- **WHEN** 开发者阅读 `docs/guides/getting-started.md`。
- **THEN** 应该能清晰了解：
    1. 如何获取和使用 API Key。
    2. 统一响应格式和错误处理逻辑。
    3. 通用查询的过滤语法。

#### Scenario: SDK Example Code
- **WHEN** 开发者运行示例脚本。
- **THEN** 脚本应该能演示完整的认证、查询和结果解析过程。

