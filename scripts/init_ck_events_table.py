import asyncio
from app.core.database import get_clickhouse_connection, init_clickhouse, close_clickhouse
from datetime import datetime, timedelta

async def init_events_table():
    print("Initializing Donghuan Events Table...")
    await init_clickhouse()
    
    table_name = "ck_fact_donghuan_event_detail_hbase"

    ddl = f"""
    CREATE TABLE IF NOT EXISTS {table_name}
    (
        rowkey                  String COMMENT 'RowKey: salt(event_id)',
        c_datacenter_id         Nullable(String) COMMENT '数据中心ID',
        c_source_ip             Nullable(String) COMMENT '源IP',
        c_source_mode           Nullable(String) COMMENT '源模式',
        event_id                Nullable(String) COMMENT '事件ID',
        resource_id             Nullable(String) COMMENT '资源ID',
        resource_name           Nullable(String) COMMENT '资源名称',
        event_type              Nullable(String) COMMENT '事件类型',
        event_level             Nullable(String) COMMENT '事件等级',
        event_message           Nullable(String) COMMENT '事件内容',
        event_time              String COMMENT '发生时间(时间戳)',
        event_status            Nullable(String) COMMENT '事件状态',
        event_location          Nullable(String) COMMENT '位置',
        event_location_name     Nullable(String) COMMENT '位置名称',
        event_device_type       Nullable(String) COMMENT '设备类型',
        event_snapshot          Nullable(String) COMMENT '快照',
        confirm_time            Nullable(String) COMMENT '确认时间',
        confirm_by              Nullable(String) COMMENT '确认人',
        confirm_description     Nullable(String) COMMENT '确认描述',
        recover_time            Nullable(String) COMMENT '恢复时间(时间戳)',
        recover_by              Nullable(String) COMMENT '恢复人',
        recover_snapshot        Nullable(String) COMMENT '恢复快照',
        remove_time             Nullable(String) COMMENT '清除时间',
        remove_by               Nullable(String) COMMENT '清除人',
        remove_description      Nullable(String) COMMENT '清除描述',
        accept_time             Nullable(String) COMMENT '受理时间',
        accept_by               Nullable(String) COMMENT '受理人'
    )
    ENGINE = ReplacingMergeTree()
    PARTITION BY toYYYYMM(toDateTime(toInt64(event_time)))
    ORDER BY (rowkey, toYYYYMM(toDateTime(toInt64(event_time))))
    PRIMARY KEY rowkey
    SETTINGS index_granularity = 8192
    """
    
    async with get_clickhouse_connection() as conn:
        async with conn.cursor() as cursor:
            print(f"Dropping table {table_name} if exists...")
            await cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
            
            print("Creating table...")
            await cursor.execute(ddl)
            
            # 2. Insert Mock Data
            print("Inserting mock data...")
            # Use a time in 2025 to match test case
            now_ts = str(int(datetime(2025, 6, 15, 12, 0, 0).timestamp()))
            
            # Using INSERT values format
            # Only filling MVP fields, others are NULL (default for Nullable)
            # rowkey, c_datacenter_id, event_id, resource_id, resource_name, event_type, event_level, event_message, event_time, event_status, event_location_name
            
            insert_sql = f"""
            INSERT INTO {table_name} 
            (rowkey, c_datacenter_id, event_id, resource_id, resource_name, event_type, event_level, event_message, event_time, event_status, event_location_name)
            VALUES
            ('evt_001', 'SH_DC_01', 'evt_id_1', 'res_001', 'Temp Sensor 1', 'alarm', '3', 'High Temperature Alarm', '{now_ts}', 'active', 'Room 101'),
            ('evt_002', 'SH_DC_01', 'evt_id_2', 'res_002', 'Door Sensor 1', 'event', '1', 'Door Opened', '{now_ts}', 'cleared', 'Room 102')
            """
            await cursor.execute(insert_sql)
            
    await close_clickhouse()
    print("Done! ✅")

if __name__ == "__main__":
    asyncio.run(init_events_table())
