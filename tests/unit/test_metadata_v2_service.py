import pytest
import json
from app.services.metadata_v2_service import MetadataV2Service
from app.core.database import init_db, close_db, get_db_connection

@pytest.fixture(autouse=True)
async def setup_db():
    await init_db()
    # 强制清理测试数据集，防止 Duplicate Entry
    async with get_db_connection() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute("DELETE FROM meta_datasets WHERE name LIKE 'test_%%' OR name LIKE 'ds_%%'")
            await conn.commit()
    yield
    await close_db()

@pytest.mark.asyncio
async def test_dataset_crud():
    """测试数据集的增删改查逻辑"""
    # 1. 创建
    ds_data = {
        "name": "test_ds_unit",
        "display_name": "Unit Test Dataset",
        "description": "Created by unit test",
        "data_source": "api_data",
        "tags": ["unit", "test"]
    }
    ds_id = await MetadataV2Service.create_dataset(ds_data)
    assert ds_id > 0

    # 2. 获取详情
    dataset = await MetadataV2Service.get_dataset_by_id(ds_id)
    assert dataset is not None
    assert dataset['name'] == "test_ds_unit"
    assert isinstance(dataset['tags'], list)
    assert "unit" in dataset['tags']

    # 3. 更新
    update_data = {"display_name": "Updated Display Name", "status": 0}
    await MetadataV2Service.update_dataset(ds_id, update_data)
    
    dataset_after = await MetadataV2Service.get_dataset_by_id(ds_id)
    assert dataset_after['display_name'] == "Updated Display Name"
    assert dataset_after['status'] == 0

    # 4. 列表查询
    all_datasets = await MetadataV2Service.get_datasets()
    assert any(d['id'] == ds_id for d in all_datasets)

    # 5. 删除
    await MetadataV2Service.delete_dataset(ds_id)
    dataset_final = await MetadataV2Service.get_dataset_by_id(ds_id)
    assert dataset_final is None

@pytest.mark.asyncio
async def test_table_and_column_persistence():
    """测试表和字段的持久化 (Upsert) 逻辑"""
    # 创建数据集环境
    ds_id = await MetadataV2Service.create_dataset({
        "name": "ds_table_test",
        "display_name": "Table Test",
        "data_source": "api_data"
    })

    try:
        # 1. 插入新表和字段
        table_data = {
            "physical_name": "test_unit_table",
            "term": "测试表",
            "description": "Desc",
            "columns": [
                {"physical_name": "col1", "term": "字段1", "type": "String", "is_primary": 1},
                {"physical_name": "col2", "term": "字段2", "type": "Int64"}
            ]
        }
        table_id = await MetadataV2Service.save_table_metadata(ds_id, table_data)
        assert table_id > 0

        # 验证插入结果
        dataset = await MetadataV2Service.get_dataset_by_id(ds_id)
        assert len(dataset['tables']) == 1
        table = dataset['tables'][0]
        assert table['physical_name'] == "test_unit_table"
        assert len(table['columns']) == 2

        # 2. 更新表和字段 (同步模式)
        updated_table_data = {
            "physical_name": "test_unit_table",
            "term": "测试表-已更新",
            "columns": [
                {"physical_name": "col1", "term": "字段1-新术语", "type": "String"}, # 更新
                {"physical_name": "col3", "term": "新字段", "type": "Float64"}      # 新增, col2 应该被删除
            ]
        }
        await MetadataV2Service.save_table_metadata(ds_id, updated_table_data)
        
        dataset_v2 = await MetadataV2Service.get_dataset_by_id(ds_id)
        table_v2 = dataset_v2['tables'][0]
        assert table_v2['term'] == "测试表-已更新"
        assert len(table_v2['columns']) == 2
        col_names = [c['physical_name'] for c in table_v2['columns']]
        assert "col1" in col_names
        assert "col3" in col_names
        assert "col2" not in col_names

    finally:
        await MetadataV2Service.delete_dataset(ds_id)

@pytest.mark.asyncio
async def test_metrics_and_relationships():
    """测试指标和关联关系的创建"""
    ds_id = await MetadataV2Service.create_dataset({"name": "ds_rel_test", "data_source": "api_data"})
    
    try:
        # 1. 创建指标
        metric_data = {
            "name": "test_metric",
            "display_name": "测试指标",
            "calculation_logic": "count(*)",
            "unit": "次"
        }
        await MetadataV2Service.create_metric(ds_id, metric_data)
        
        # 2. 创建关联关系需要先有表
        t1_id = await MetadataV2Service.save_table_metadata(ds_id, {"physical_name": "tab1", "term": "T1", "columns": []})
        t2_id = await MetadataV2Service.save_table_metadata(ds_id, {"physical_name": "tab2", "term": "T2", "columns": []})
        
        rel_data = {
            "source_table_id": t1_id,
            "target_table_id": t2_id,
            "join_condition": "tab1.id = tab2.ref_id",
            "join_type": "LEFT JOIN"
        }
        await MetadataV2Service.create_relationship(ds_id, rel_data)

        # 验证详情
        dataset = await MetadataV2Service.get_dataset_by_id(ds_id)
        assert len(dataset['metrics']) == 1
        assert len(dataset['relationships']) == 1
        assert dataset['metrics'][0]['name'] == "test_metric"
        assert dataset['relationships'][0]['source_table'] == "tab1"

    finally:
        await MetadataV2Service.delete_dataset(ds_id)
