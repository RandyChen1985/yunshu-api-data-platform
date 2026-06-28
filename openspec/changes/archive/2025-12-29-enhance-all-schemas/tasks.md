## 1. Schema 优化
- [ ] 1.1 修改 `app/api/v1/schemas/data.py`，为所有核心模型添加 `example` 和详细 `description`。
- [ ] 1.2 确保 `BaseResponse` 和 `ErrorResponse` 的文档也得到更新。

## 2. 验证
- [ ] 2.1 运行 API 测试，确保 Schema 修改未破坏现有反序列化逻辑。
- [ ] 2.2 (手动) 确认 OpenAPI JSON 中包含新的示例值。
