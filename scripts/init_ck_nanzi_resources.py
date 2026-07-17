import asyncio
from app.core.config import settings
from asynch.pool import Pool

TABLE_ROOMS = "ck_fact_yunshu_resroom_hbase"
TABLE_RACKS = "ck_fact_yunshu_resjj_hbase"
TABLE_POINTS = "ck_fact_yunshu_devicepoint_hbase"

async def init_data():
    print(f"Connecting to ClickHouse at {settings.CLICKHOUSE_HOST}:{settings.CLICKHOUSE_PORT}...")
    
    pool = Pool(
        host=settings.CLICKHOUSE_HOST,
        port=settings.CLICKHOUSE_PORT,
        database=settings.CLICKHOUSE_DB,
        user=settings.CLICKHOUSE_USER,
        password=settings.CLICKHOUSE_PASSWORD,
    )

    async with pool.connection() as conn:
        async with conn.cursor() as cursor:
            # 1. Create Tables
            print("Creating tables...")
            
            # Rooms DDL
            print(f"Dropping and Creating {TABLE_ROOMS}...")
            await cursor.execute(f"DROP TABLE IF EXISTS {settings.CLICKHOUSE_DB}.{TABLE_ROOMS}")
            await cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {settings.CLICKHOUSE_DB}.{TABLE_ROOMS} (
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

            # Racks DDL
            print(f"Dropping and Creating {TABLE_RACKS}...")
            await cursor.execute(f"DROP TABLE IF EXISTS {settings.CLICKHOUSE_DB}.{TABLE_RACKS}")
            await cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {settings.CLICKHOUSE_DB}.{TABLE_RACKS} (
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

            # Device Points DDL
            print(f"Dropping and Creating {TABLE_POINTS}...")
            await cursor.execute(f"DROP TABLE IF EXISTS {settings.CLICKHOUSE_DB}.{TABLE_POINTS}")
            await cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {settings.CLICKHOUSE_DB}.{TABLE_POINTS} (
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
            
            # 2. Insert Mock Data
            print("Inserting mock data...")
            
            # Rooms Data
            rooms_data = [
                {"rowkey": "ROOM_001", "jfbm": "SH_JQ", "jfmc": "Shanghai Jinqiao", "ywzx": "East China", "gsbs": "Yovole"},
                {"rowkey": "ROOM_002", "jfbm": "BJ_DC", "jfmc": "Beijing DataCenter", "ywzx": "North China", "gsbs": "Yovole"},
            ]
            await cursor.execute(f"""
                INSERT INTO {settings.CLICKHOUSE_DB}.{TABLE_ROOMS} (rowkey, jfbm, jfmc, ywzx, gsbs) VALUES
            """, rooms_data)
            
            # Racks Data
            racks_data = [
                {"rowkey": "RACK_001", "jfmc": "Shanghai Jinqiao", "jjbm": "A01", "jjzt": "Used", "kh": "CUST_001", "khmc": "Tech Corp"},
                {"rowkey": "RACK_002", "jfmc": "Shanghai Jinqiao", "jjbm": "A02", "jjzt": "Available", "kh": "", "khmc": ""},
                {"rowkey": "RACK_003", "jfmc": "Beijing DataCenter", "jjbm": "B01", "jjzt": "Used", "kh": "CUST_002", "khmc": "Finance Inc"},
            ]
            await cursor.execute(f"""
                INSERT INTO {settings.CLICKHOUSE_DB}.{TABLE_RACKS} (rowkey, jfmc, jjbm, jjzt, kh, khmc) VALUES
            """, racks_data)

            # Device Points Data
            points_data = [
                {"rowkey": "POINT_001", "jf": "Shanghai Jinqiao", "jjbm": "A01", "dwid": "P_01_01", "dwlx": "Power"},
                {"rowkey": "POINT_002", "jf": "Shanghai Jinqiao", "jjbm": "A01", "dwid": "P_01_02", "dwlx": "Network"},
                {"rowkey": "POINT_003", "jf": "Beijing DataCenter", "jjbm": "B01", "dwid": "P_02_01", "dwlx": "Cooling"},
            ]
            await cursor.execute(f"""
                INSERT INTO {settings.CLICKHOUSE_DB}.{TABLE_POINTS} (rowkey, jf, jjbm, dwid, dwlx) VALUES
            """, points_data)

            print("Data insertion complete.")
            
    await pool.shutdown()

if __name__ == "__main__":
    asyncio.run(init_data())
