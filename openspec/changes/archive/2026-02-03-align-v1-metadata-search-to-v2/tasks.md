## 1. Request & Response Schema Update

- [x] 1.1 在 `app/api/v1/endpoints/meta.py` 中更新 `SearchRequest` 模型，添加 `enable_rerank` 字段并完善 `Field` 描述。
- [x] 1.2 定义 `ExternalSearchResponse` 模型，确保 Swagger 能正确展示返回的 JSON 结构（data, count, dataset_ids）。

## 2. API Logic Refactoring

- [x] 2.1 重构 `external_search_metadata` 函数，增加对 `search_type="semantic"` 的分支处理。
- [x] 2.2 调用 `VectorService.semantic_search` 实现向量检索（支持传入 `enable_rerank`）。
- [x] 2.3 废弃全量数据集 YAML 生成，实现基于 `results` 命中的“原子化片段提取”逻辑（逻辑同步自 V2）。
- [x] 2.4 实现最终 YAML 的去重合并与结果返回，确保不泄露 `debug_logs`。

## 3. Testing & Verification

- [x] 3.1 编写新的自动化测试脚本 `tests/api/v1/test_meta_search_enhanced.py`，覆盖 keyword 和 semantic（含 rerank）场景。
- [x] 3.2 运行全量测试 `tests/run_tests.sh` 确保无回归错误。
- [x] 3.3 启动服务验证 Swagger UI (`/docs`) 中的 V1 检索接口文档是否完整、准确。
