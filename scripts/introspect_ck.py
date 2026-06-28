import asyncio
from app.core import database
from app.services.meta_service import MetaService

async def main():
    await database.init_clickhouse()
    service = MetaService()
    
    tables = [
        "ck_fact_donghuan_real_metric_hbase",
        "ck_fact_donghuan_event_detail_hbase",
        "ck_fact_yunshu_resroom_hbase",
        "ck_fact_yunshu_resjj_hbase",
        "ck_fact_yunshu_devicepoint_hbase",
        # Potential CCG tables
        "ck_fact_ccg_resource_hbase",
        "ck_fact_ccg_vm_hbase",
        "ck_fact_ccg_container_hbase"
    ]
    
    print("--- ClickHouse Schema Introspection ---")
    for table in tables:
        try:
            print(f"\nTable: {table}")
            columns = await service.get_columns("clickhouse", table)
            for col in columns:
                print(f"  - {col['name']} ({col['type']}): {col['comment']}")
        except Exception as e:
            print(f"  Error fetching table {table}: {e}")
    
    await database.close_clickhouse()

if __name__ == "__main__":
    asyncio.run(main())
