## Context

目前公开 API (V1) 的 `/search` 端点逻辑过于陈旧，仅支持 SQL `LIKE` 匹配，且返回数据颗粒度太大（以数据集为单位返回 YAML），不符合当前精细化 RAG 上下文的要求。

## Goals / Non-Goals

**Goals:**
- 将 V1 检索接口的底层逻辑与 V2 对齐，支持 `semantic` 和 `rerank` 模式。
- 实现原子化组装逻辑，仅返回命中的表/指标 YAML 片段。
- 保持向后兼容（默认 `search_type` 为 `keyword`）。

**Non-Goals:**
- 不返回 `debug_logs` 调试日志。
- 不修改 V1 的身份验证与资源权限逻辑。

## Decisions

### 1. 逻辑克隆而非抽象封装
**决策**：在 `app/api/v1/endpoints/meta.py` 中直接复刻 V2 的检索组装逻辑。
**理由**：虽然抽象公共方法更优雅，但 V1 和 V2 在响应结构（是否有 `debug_logs`）和权限校验上有本质区别。直接克隆逻辑可以最快实现目标且避免破坏 V2 稳定的 Portal 接口。

### 2. 移除调试信息
**决策**：在 V1 代码实现中彻底剔除 `debug_logs.append(...)` 相关调用。
**理由**：外部调用方通常只需要最终的上下文结果，过多的路径日志可能暴露内部架构细节且增加不必要的传输负担。

### 3. 请求模型升级
**决策**：更新 `SearchRequest` 增加 `enable_rerank` 字段。
**理由**：对齐 V2 的参数集，允许外部高级调用方开启精排以获得更好的 Context。

## Risks / Trade-offs

- **[Risk] 响应时间增加**：开启 `semantic` 或 `rerank` 模式后，接口耗时会从毫秒级升至百毫秒甚至秒级（取决于 Rerank 模型）。
  - **Mitigation**: 文档中明确标注语义检索的性能开销。
- **[Risk] 上下文断裂**：如果外部调用方习惯了获取整个数据集的 YAML，切换到原子片段后，LLM 可能因为缺少某些关联表的信息而产生幻觉。
  - **Mitigation**: 保持 V1 原有的 `dataset_ids` 返回，调用方可按需请求详情。
