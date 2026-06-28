# 设计文档: 数据适配器模块化 (Data Adapter Modularization)

## 背景 (Context)
数据 API 平台需要支持多种底层数据引擎（ClickHouse, MySQL, HBase）。目前所有逻辑都集中在单个文件 `data_adapter.py` 中，这违反了单一职责原则，并且难以添加新的数据源。

## 目标与非目标 (Goals / Non-Goals)
- **目标**:
    - 定义严格的 `DataSourceAdapter` 接口。
    - 实现符合该接口的 `ClickHouseAdapter`。
    - 提供用于获取适配器的工厂方法。
    - 确保现有的 ClickHouse 查询无回归。
- **非目标**:
    - 在本次变更中实现 MySQL 或 HBase 适配器（仅做脚手架和架构铺垫）。

## 决策 (Decisions)
- **决策**: 使用 Python 的 `abc` 模块定义接口 (`BaseAdapter`)。
    - **原因**: 强制子类实现 `execute` 和 `execute_summary` 方法。
- **决策**: 将 `LogicalQuery` 和 `ResultSet` 数据类保留在 `app/schemas` 或 `app/services/data_adapter/models.py` 中。
    - **原因**: 这些是跨层使用的共享数据结构。将它们移动到适配器包内的 `models` 子模块可以保持高内聚。

## 风险与权衡 (Risks / Trade-offs)
- **风险**: 迁移过程中现有 API 端点可能出现导入错误。
    - **缓解措施**: 使用 `task_boundary` 仔细搜索 `app.services.data_adapter` 的所有引用，并原子性地进行更新。

## 迁移计划 (Migration Plan)
1. 创建新的包结构。
2. 移动代码。
3. 修复导入路径。
4. 运行测试。
