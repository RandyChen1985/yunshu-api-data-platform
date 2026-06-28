import asyncio
import time
import random
from app.core import database
from app.core.config import settings
from asynch.connection import Connection

# Schema Definition
TABLE_NAME = "ck_fact_donghuan_real_metric_hbase"

async def init_data():
    print(f"Connecting to ClickHouse at {settings.CLICKHOUSE_HOST}:{settings.CLICKHOUSE_PORT}...")
    
    async with database.get_clickhouse_connection() as conn:
        async with conn.cursor() as cursor:
            print(f"Dropping table {TABLE_NAME} if exists...")
            await cursor.execute(f"DROP TABLE IF EXISTS {settings.CLICKHOUSE_DB}.{TABLE_NAME}")

            print(f"Creating table {TABLE_NAME}...")
            ddl = f"""
            CREATE TABLE IF NOT EXISTS {settings.CLICKHOUSE_DB}.{TABLE_NAME}
            (
                rowkey                  String COMMENT '主键',
                c_datacenter_id         Nullable(String) COMMENT '数据中心ID',
                c_source_ip             Nullable(String) COMMENT '源IP',
                c_source_mode           Nullable(String) COMMENT '源模式',
                resource_id             Nullable(String) COMMENT '资源ID',
                metric_name             Nullable(String) COMMENT '指标名称',
                metric_value            Nullable(String) COMMENT '指标值',
                metric_unit             Nullable(String) COMMENT '指标单位',
                metric_time             String COMMENT '指标时间(时间戳)',
                status                  Nullable(String) COMMENT '状态'
            )
            ENGINE = ReplacingMergeTree()
            PARTITION BY toYYYYMMDD(toDateTime(toInt64(metric_time)))
            ORDER BY (rowkey, toYYYYMMDD(toDateTime(toInt64(metric_time))))
            PRIMARY KEY rowkey
            SETTINGS index_granularity = 8192
            """
            await cursor.execute(ddl)

            # Insert Mock Data
            print("Inserting mock data...")
            current_time = int(time.time())
            data = []
            
            resources = [
                ("SH_JQ_01", "Temp-Sensor-001", "温度", "℃", 20, 30),
                ("SH_JQ_01", "Humi-Sensor-001", "湿度", "%", 40, 60),
                ("BJ_DC_02", "Power-Meter-002", "有功功率", "kW", 100, 500),
                ("SH_LG_03", "UPS-Status-003", "输出电压", "V", 220, 240)
            ]

            for dc_id, res_id, metric, unit, min_v, max_v in resources:
                # Generate 100 points for each resource
                for i in range(100):
                     t = current_time - (i * 60) # Backwards 100 minutes
                     val = round(random.uniform(min_v, max_v), 2)
                     row = {
                         "rowkey": f"{res_id}.{metric}",
                         "c_datacenter_id": dc_id,
                         "c_source_ip": "192.168.1.1",
                         "c_source_mode": "MOCK",
                         "resource_id": res_id,
                         "metric_name": metric,
                         "metric_value": str(val),
                         "metric_unit": unit,
                         "metric_time": str(t),
                         "status": "normal"
                     }
                     data.append(row)

            # Bulk Insert
            insert_sql = f"""
            INSERT INTO {settings.CLICKHOUSE_DB}.{TABLE_NAME} 
            (rowkey, c_datacenter_id, c_source_ip, c_source_mode, resource_id, metric_name, metric_value, metric_unit, metric_time, status)
            VALUES
            """
            await cursor.execute(insert_sql, data)
            print(f"Inserted {len(data)} rows.")

    await database.close_clickhouse()

if __name__ == "__main__":
    asyncio.run(init_data())
