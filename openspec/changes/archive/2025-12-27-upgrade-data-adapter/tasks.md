## 1. 准备工作 (Preparation)
- [x] 1.1 创建 `app/services/data_adapter/` 目录和 `__init__.py`。
- [x] 1.2 识别所有使用了 `app.services.data_adapter` 的代码位置。

## 2. 重构执行 (Refactoring)
- [x] 2.1 提取共享模型 (`LogicalQuery`, `ResultSet`) 到 `app/services/data_adapter/models.py`。
- [x] 2.2 在 `app/services/data_adapter/base.py` 中定义接口 `DataSourceAdapter`。
- [x] 2.3 将 `ClickHouseAdapter` 逻辑移动到 `app/services/data_adapter/clickhouse.py`。
- [x] 2.4 在 `app/services/data_adapter/factory.py` 中实现工厂方法 `get_adapter` (并在 `__init__.py` 中暴露)。
- [x] 2.5 移除原本的 `app/services/data_adapter.py`。

## 3. 集成与修复 (Integration)
- [x] 3.1 更新 `app/api/v1/endpoints/resources_donghuan.py` 中的导入。
- [x] 3.2 更新 `app/api/v1/endpoints/resources_nanzi.py` 中的导入。
- [x] 3.3 更新其他所有相关位置的导入。

## 4. 验证 (Verification)
- [x] 4.1 运行 `pytest tests/test_resources_donghuan.py` 确保无回归。
- [x] 4.2 运行 `pytest tests/test_resources_nanzi.py` 确保无回归。
