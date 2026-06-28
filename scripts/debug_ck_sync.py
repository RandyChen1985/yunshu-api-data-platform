from clickhouse_driver import Client
from datetime import datetime

HOST = 'localhost'
PORT = 9000
CREDS = [
    ('default', '', 'default'),
    ('default', '', 'yovole_ck_prod'),
    ('yovole_ck_prod', '', 'default'),
]

print(f"Testing ClickHouse-Driver at {HOST}:{PORT}")

for user, password, db in CREDS:
    print(f"Trying User='{user}', Pass='{password}', DB='{db}' ... ", end="")
    try:
        client = Client(host=HOST, port=PORT, user=user, password=password, database=db)
        ver = client.execute("SELECT version()")
        print(f"SUCCESS! ✅ Version: {ver[0][0]}")
    except Exception as e:
        print(f"FAILED ❌ {e}")
