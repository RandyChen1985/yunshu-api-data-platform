## 1. Backend Service Refactoring (MetaService)

- [x] 1.1 在 `app/services/meta_service.py` 中扩展 `get_schema_context` 方法，增加可选的 `prompt` 参数。
- [x] 1.2 实现“语义优先”的元数据提取逻辑：根据 `tables` 列表，优先从 `meta_v2` 库中组装 YAML 片段。
- [x] 1.3 实现“语义自动召回”逻辑：若 `tables` 为空但存在 `prompt`，调用 `VectorService.semantic_search` 自动锁定表/指标。
- [x] 1.4 实现物理结构保底 (Fallback)：若语义库查无此表，则调用适配器获取原始 Schema 并转换为 YAML 格式。

## 2. API & Controller Updates (Lab Endpoints)

- [x] 2.1 修改 `app/api/portal/endpoints/lab.py` 中的 `ai_generate_sql` 和 `ai_edit_sql`，将用户提问透传给 `get_schema_context`。
- [x] 2.2 更新 `AIGenerateRequest` 和 `AIEditRequest` 模型，确保 Prompt 字段在后端可用。

## 3. Frontend UI Enhancement (SQLLab)

- [x] 3.1 在 `frontend/src/components/sqllab/SchemaSidebar.vue` 顶部增加“智能关联上下文”开关（Toggle Switch）。
- [x] 3.2 调整 `frontend/src/views/SQLLab.vue` 的状态管理，根据开关状态决定是否在 AI 请求中发送已勾选的 `selectedTables`。
- [x] 3.3 优化 AI 输入框的占位符提示，引导用户在“自动关联”开启时直接输入业务问题。

## 4. Verification & Prompt Tuning

- [x] 4.1 编写单元测试验证 `MetaService.get_schema_context` 在不同参数组合下的返回结果。
- [x] 4.2 调整后端 AI 提示词模板，使其更好地理解新注入的 YAML 业务语义（如枚举、指标）。