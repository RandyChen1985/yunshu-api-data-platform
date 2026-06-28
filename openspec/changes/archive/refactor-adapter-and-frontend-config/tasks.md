# 任务清单：重构适配器与前端配置

## 后端重构 (ClickHouseAdapter)
- [ ] 定义 `RESOURCE_MAPPING` 配置结构，包含表名、字段列表和排序默认值 <!-- id: 0 -->
- [ ] 重构 `_build_where` 方法（如果需要）以适配通用配置 <!-- id: 1 -->
- [ ] 重构 `execute` 方法，实现基于配置的动态 SQL 构建和结果集映射 <!-- id: 2 -->
- [ ] 验证现有单元测试（`tests/api/v1/test_resources_*.py`），确保重构不破坏现有功能 <!-- id: 3 -->

## 前端优化 (Frontend)
- [ ] 修改 `frontend/vite.config.ts`，添加 `@` 别名配置 <!-- id: 4 -->
- [ ] 修改 `frontend/tsconfig.json` (或 `tsconfig.app.json`)，添加 `paths` 映射 <!-- id: 5 -->
- [ ] (可选) 挑选 1-2 个文件将相对路径引用改为 `@` 引用，验证配置是否生效 <!-- id: 6 -->
