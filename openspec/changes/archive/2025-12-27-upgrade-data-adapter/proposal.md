# 变更提案: 升级数据适配层 (Upgrade Data Adapter Layer)

## Why
目前的 `data_adapter.py` 是一个单文件模块，混合了接口定义与 ClickHouse 的具体实现细节。鉴于本平台定位为“通用数据 API 平台”，旨在支持 ClickHouse、MySQL 和 HBase 等多种数据源，这种单体结构难以扩展。我们需要将接口与实现解耦，以便轻松扩展新的数据源。

## What Changes
- **重构 (Refactor)**: 将单文件模块 `app/services/data_adapter.py` 转换为 Python 包 `app/services/data_adapter/`。
- **接口 (Interface)**: 定义清晰的 `BaseAdapter` 抽象基类。
- **实现 (Implementation)**: 将 `ClickHouseAdapter` 隔离到独立的模块中。
- **工厂模式 (Factory)**: 实现工厂模式，根据配置或请求实例化具体的适配器。
- **类型增强 (Typing)**: 增强 `Query` 和 `ResultSet` 对象的类型提示。

## 影响范围 (Impact)
- **受影响 Spec**: `data-adapter` (新能力)
- **受影响代码**: 
    - `app/services/data_adapter.py` (将被移除/转换为包)
    - `app/services/data_adapter/base.py` (新增)
    - `app/services/data_adapter/clickhouse.py` (新增)
    - `app/services/data_adapter/factory.py` (新增)
    - `app/api/v1/endpoints/*.py` (需要更新导入路径)
