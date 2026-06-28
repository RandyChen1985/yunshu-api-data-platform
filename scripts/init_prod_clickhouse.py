import asyncio
import time
import random
from datetime import datetime
from app.core.config import settings
from asynch.pool import Pool

NEW_DB = "yovole_dm_clickhouse_prod"

# Define connection settings safely
CH_HOST = getattr(settings, "CLICKHOUSE_HOST", "localhost")
CH_PORT = getattr(settings, "CLICKHOUSE_PORT", 9000)
CH_USER = getattr(settings, "CLICKHOUSE_USER", "admin")
CH_PASSWORD = getattr(settings, "CLICKHOUSE_PASSWORD", "admin123")

async def init_prod_db():
    print(f"Connecting to ClickHouse at {CH_HOST}:{CH_PORT}...")
    
    # Connect to default DB first to create the new one
    pool = Pool(
        host=CH_HOST,
        port=CH_PORT,
        database="default",
        user=CH_USER,
        password=CH_PASSWORD,
    )
    
    async with pool.connection() as conn:
        async with conn.cursor() as cursor:
            print(f"Creating database {NEW_DB}...")
            await cursor.execute(f"CREATE DATABASE IF NOT EXISTS {NEW_DB}")
    
    await pool.shutdown()
    
    # Now connect to the new DB
    pool = Pool(
        host=CH_HOST,
        port=CH_PORT,
        database=NEW_DB,
        user=CH_USER,
        password=CH_PASSWORD,
    )
    
    async with pool.connection() as conn:
        async with conn.cursor() as cursor:
            # --- 1. Real Metrics ---
            table_metrics = "ck_fact_donghuan_real_metric_hbase"
            print(f"Initializing {table_metrics}...")
            await cursor.execute(f"DROP TABLE IF EXISTS {NEW_DB}.{table_metrics}")
            await cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {NEW_DB}.{table_metrics}
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
            """)
            
            # Insert Metrics Data
            current_time = int(time.time())
            data_metrics = []
            resources = [
                ("SH_JQ_01", "Temp-Sensor-001", "温度", "℃", 20, 30),
                ("SH_JQ_01", "Humi-Sensor-001", "湿度", "%", 40, 60),
                ("BJ_DC_02", "Power-Meter-002", "有功功率", "kW", 100, 500),
                ("SH_LG_03", "UPS-Status-003", "输出电压", "V", 220, 240)
            ]
            for dc_id, res_id, metric, unit, min_v, max_v in resources:
                for i in range(100):
                     t = current_time - (i * 60)
                     val = round(random.uniform(min_v, max_v), 2)
                     data_metrics.append({
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
                     })
            await cursor.execute(f"""
            INSERT INTO {NEW_DB}.{table_metrics} 
            (rowkey, c_datacenter_id, c_source_ip, c_source_mode, resource_id, metric_name, metric_value, metric_unit, metric_time, status)
            VALUES
            """, data_metrics)


            # --- 2. Events ---
            table_events = "ck_fact_donghuan_event_detail_hbase"
            print(f"Initializing {table_events}...")
            await cursor.execute(f"DROP TABLE IF EXISTS {NEW_DB}.{table_events}")
            await cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {NEW_DB}.{table_events}
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
            """)
            
            now_ts = str(int(datetime(2025, 6, 15, 12, 0, 0).timestamp()))
            await cursor.execute(f"""
            INSERT INTO {NEW_DB}.{table_events} 
            (rowkey, c_datacenter_id, event_id, resource_id, resource_name, event_type, event_level, event_message, event_time, event_status, event_location_name)
            VALUES
            ('evt_001', 'SH_DC_01', 'evt_id_1', 'res_001', 'Temp Sensor 1', 'alarm', '3', 'High Temperature Alarm', '{now_ts}', 'active', 'Room 101'),
            ('evt_002', 'SH_DC_01', 'evt_id_2', 'res_002', 'Door Sensor 1', 'event', '1', 'Door Opened', '{now_ts}', 'cleared', 'Room 102')
            """)


            # --- 3. Yunshu Resources ---
            table_rooms = "ck_fact_yunshu_resroom_hbase"
            table_racks = "ck_fact_yunshu_resjj_hbase"
            table_points = "ck_fact_yunshu_devicepoint_hbase"
            
            print(f"Initializing Yunshu Tables...")
            # Rooms
            await cursor.execute(f"DROP TABLE IF EXISTS {NEW_DB}.{table_rooms}")
            await cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {NEW_DB}.{table_rooms} (
                    rowkey String,
                    id Nullable(String),
                    ywzx Nullable(String),
                    jgzs Nullable(String),
                    modedatamodifydatetime Nullable(String),
                    sjjfs Nullable(String),
                    sykss Nullable(String),
                    gxqy Nullable(String),
                    jfmc Nullable(String),
                    belongmidperiod Nullable(String),
                    yeszjid Nullable(String),
                    jfbm Nullable(String),
                    modeuuid Nullable(String),
                    jfjc Nullable(String),
                    bkys Nullable(String),
                    yqys Nullable(String),
                    yjfs Nullable(String),
                    dz Nullable(String),
                    form_biz_id Nullable(String),
                    outkey Nullable(String),
                    belongship Nullable(String),
                    nbjys Nullable(String),
                    co Nullable(String),
                    modedatacreatetime Nullable(String),
                    bz Nullable(String),
                    requestid Nullable(String),
                    modedatamodifier Nullable(String),
                    kss Nullable(String),
                    cc Nullable(String),
                    kqzt Nullable(String),
                    gsbs Nullable(String),
                    modedatacreatedate Nullable(String),
                    px Nullable(String),
                    khmc Nullable(String),
                    modedatacreater Nullable(String),
                    jfzdl Nullable(String),
                    dhjkkqzt Nullable(String),
                    formmodeid Nullable(String),
                    modedatacreatertype Nullable(String)
                ) ENGINE = ReplacingMergeTree() ORDER BY rowkey
            """)
             # Racks
            await cursor.execute(f"DROP TABLE IF EXISTS {NEW_DB}.{table_racks}")
            await cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {NEW_DB}.{table_racks} (
                    rowkey String,
                    id Nullable(String),
                    jjbmyh Nullable(String),
                    kh Nullable(String),
                    akg Nullable(String),
                    form_biz_id Nullable(String),
                    ywzx Nullable(String),
                    modedatacreatedate Nullable(String),
                    nbjjsfsd Nullable(String),
                    sfwc Nullable(String),
                    ac19 Nullable(String),
                    wdslaxx Nullable(String),
                    dhzt Nullable(String),
                    modedatacreatertype Nullable(String),
                    bkgzt Nullable(String),
                    formmodeid Nullable(String),
                    ac13 Nullable(String),
                    jfmc Nullable(String),
                    sdslaxx Nullable(String),
                    col Nullable(String),
                    mk Nullable(String),
                    ztsm Nullable(String),
                    jjzt Nullable(String),
                    akgzt Nullable(String),
                    modeuuid Nullable(String),
                    jjbm Nullable(String),
                    modedatamodifydatetime Nullable(String),
                    sdzt Nullable(String),
                    jjbmyys Nullable(String),
                    wdslasx Nullable(String),
                    bkg Nullable(String),
                    modedatacreater Nullable(String),
                    bc13 Nullable(String),
                    requestid Nullable(String),
                    modedatamodifier Nullable(String),
                    htbm Nullable(String),
                    bzdl Nullable(String),
                    sddl Nullable(String),
                    pdulx Nullable(String),
                    outkey Nullable(String),
                    zzkh Nullable(String),
                    apdu Nullable(String),
                    sfzy Nullable(String),
                    jjlx Nullable(String),
                    khmc Nullable(String),
                    bpdu Nullable(String),
                    dhztrq Nullable(String),
                    xnjj Nullable(String),
                    sdrq Nullable(String),
                    bc19 Nullable(String),
                    sdslasx Nullable(String),
                    srlx Nullable(String),
                    lc Nullable(String),
                    modedatacreatetime Nullable(String),
                    zzkhbm Nullable(String),
                    jfbm Nullable(String)
                ) ENGINE = ReplacingMergeTree() ORDER BY rowkey
            """)
             # Points
            await cursor.execute(f"DROP TABLE IF EXISTS {NEW_DB}.{table_points}")
            await cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {NEW_DB}.{table_points} (
                    rowkey String,
                    id Nullable(String),
                    modedatamodifier Nullable(String),
                    dwmc Nullable(String),
                    modedatacreatetime Nullable(String),
                    modedatacreatertype Nullable(String),
                    szwz Nullable(String),
                    jf Nullable(String),
                    modedatacreater Nullable(String),
                    modedatamodifydatetime Nullable(String),
                    sztd Nullable(String),
                    requestid Nullable(String),
                    jc Nullable(String),
                    dyztid Nullable(String),
                    xgsb Nullable(String),
                    modeuuid Nullable(String),
                    form_biz_id Nullable(String),
                    sbjc Nullable(String),
                    jjbm Nullable(String),
                    dwid Nullable(String),
                    formmodeid Nullable(String),
                    szlc Nullable(String),
                    dwlx Nullable(String),
                    modedatacreatedate Nullable(String),
                    szmk Nullable(String),
                    metric_time Nullable(String),
                    metric_value Nullable(String)
                ) ENGINE = ReplacingMergeTree() ORDER BY rowkey
            """)

            # Data
            rooms_data = [
                {"rowkey": "ROOM_001", "jfbm": "SH_JQ", "jfmc": "Shanghai Jinqiao", "ywzx": "East China", "gsbs": "Yovole"},
                {"rowkey": "ROOM_002", "jfbm": "BJ_DC", "jfmc": "Beijing DataCenter", "ywzx": "North China", "gsbs": "Yovole"},
            ]
            await cursor.execute(f"INSERT INTO {NEW_DB}.{table_rooms} (rowkey, jfbm, jfmc, ywzx, gsbs) VALUES", rooms_data)
            
            racks_data = [
                {"rowkey": "RACK_001", "jfmc": "Shanghai Jinqiao", "jjbm": "A01", "jjzt": "Used", "kh": "CUST_001", "khmc": "Tech Corp"},
                {"rowkey": "RACK_002", "jfmc": "Shanghai Jinqiao", "jjbm": "A02", "jjzt": "Available", "kh": "", "khmc": ""},
                {"rowkey": "RACK_003", "jfmc": "Beijing DataCenter", "jjbm": "B01", "jjzt": "Used", "kh": "CUST_002", "khmc": "Finance Inc"},
            ]
            await cursor.execute(f"INSERT INTO {NEW_DB}.{table_racks} (rowkey, jfmc, jjbm, jjzt, kh, khmc) VALUES", racks_data)

            points_data = [
                {"rowkey": "POINT_001", "jf": "Shanghai Jinqiao", "jjbm": "A01", "dwid": "P_01_01", "dwlx": "Power"},
                {"rowkey": "POINT_002", "jf": "Shanghai Jinqiao", "jjbm": "A01", "dwid": "P_01_02", "dwlx": "Network"},
                {"rowkey": "POINT_003", "jf": "Beijing DataCenter", "jjbm": "B01", "dwid": "P_02_01", "dwlx": "Cooling"},
            ]
            await cursor.execute(f"INSERT INTO {NEW_DB}.{table_points} (rowkey, jf, jjbm, dwid, dwlx) VALUES", points_data)

            print("✅ Production Database Initialized Successfully!")

    await pool.shutdown()

if __name__ == "__main__":
    asyncio.run(init_prod_db())