# Change: Enhance All Schemas

## Why
为了进一步提升开发者体验，特别是为了让 AI Agent 能更准确地理解和调用 API，我们需要将详细的文档覆盖到所有的 Pydantic Schema 中。目前部分 Response Model 缺乏 `example` 和详细描述，导致 OpenAPI 文档的 Example Value 部分不够直观。

## What Changes
- **MODIFIED**: `app/api/v1/schemas/data.py`
    - 为 `YunshuRoomResponse`, `YunshuRackResponse`, `YunshuDevicePointResponse` 等模型的所有字段添加 `example`。
    - 丰富字段的 `description`，增加业务语义说明。
    - 为 `BaseResponse` 增加通用的响应示例。

## Impact
- **影响范围**: OpenAPI 文档 (`/openapi.json`) 和 Swagger UI。
- **风险**: 无逻辑风险，仅影响文档生成。
