## 1. 定义 Schema
- [ ] 1.1 创建 `app/api/v1/schemas/ccg.py`，包含 `CCGResourceResponse`, `CCGVirtualMachineResponse`, `CCGContainerResponse` 等模型，并附带详细 example。

## 2. 更新 Endpoints
- [ ] 2.1 修改 `app/api/v1/endpoints/ccg.py`，引用上述模型作为 `response_model`，并构造符合 Schema 的模拟返回数据。

## 3. 验证
- [ ] 3.1 运行测试（如果有针对 CCG 的测试，或者新建一个简单的测试）。
