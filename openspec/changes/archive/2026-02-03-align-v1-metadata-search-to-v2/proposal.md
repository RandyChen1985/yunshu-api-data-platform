## Why

目前对外公开的 V1 元数据检索接口仅支持简单的 MySQL LIKE 关键词匹配，且返回结果以“数据集”为单位（返回整个数据集的 YAML），存在检索精度低、上下文冗余大的问题。为了让外部调用方也能享受 V2 版本的语义搜索和两阶段精排（Rerank）能力，需要对 V1 接口进行能力对齐。

## What Changes

- **功能对齐**：为 V1 `/search` 接口增加对 `search_type="semantic"` 的支持。
- **参数扩展**：在请求模型中增加 `enable_rerank` 布尔参数（默认为 `false`）。
- **组装策略升级**：将 V1 现有的“数据集全量组装”逻辑替换为 V2 的“原子化片段组装”逻辑，仅返回与查询高度相关的表/指标定义。
- **响应优化**：与 V2 不同，V1 接口将不返回 `debug_logs`，以保持 API 的纯净和安全性。

## Capabilities

### New Capabilities
<!-- 无 -->

### Modified Capabilities
- `semantic-metadata`: 更新 V1 API 的规格定义，支持语义模式与 Rerank。

## Impact

- `app/api/v1/endpoints/meta.py`: 核心修改点，重写检索与组装流程。
- `app/schemas/`: 如果 V1 使用了独立的 Pydantic 模型，需同步更新。
