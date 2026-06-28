import asyncio
from asynch.connection import Connection

async def init_table():
    try:
        conn = Connection(
            host='localhost', 
            port=9000, 
            user='admin', 
            password='admin123', 
            database='default'
        )
        await conn.connect()
        async with conn.cursor() as cursor:
            # Create Table
            ddl = """
            CREATE TABLE IF NOT EXISTS default.ck_fact_donghuan_real_metric_hbase
            (
                rowkey                  String,
                c_datacenter_id         Nullable(String),
                c_source_ip             Nullable(String),
                c_source_mode           Nullable(String),
                resource_id             Nullable(String),
                metric_name             Nullable(String),
                metric_value            Nullable(String),
                metric_unit             Nullable(String),
                metric_time             String,
                status                  Nullable(String)
            )
            ENGINE = Memory
            """
            await cursor.execute(ddl)
            print("Table created successfully! ✅")

            # Insert a dummy record for the test
            # test_generic_query_success expects:
            # metric_name = "temperature_rack_inlet"
            # metric_value > "20"
            
            insert_sql = """
            INSERT INTO default.ck_fact_donghuan_real_metric_hbase 
            (rowkey, metric_name, metric_value, metric_time) 
            VALUES 
            """
            data = [('test_rk_1', 'temperature_rack_inlet', '25.5', '1704067200')]
            await cursor.execute(insert_sql, data)
            print("Seed record inserted! ✅")

        await conn.close()
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(init_table())
