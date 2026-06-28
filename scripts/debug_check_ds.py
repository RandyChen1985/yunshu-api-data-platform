import asyncio
import json
from app.core.database import init_db, get_db_connection, close_db
from app.services.datasource_service import DataSourceService

async def check():
    try:
        await init_db()
        ds_list = await DataSourceService.list_datasources()
        for ds in ds_list:
            print(f"ID: {ds.id}, Name: {ds.source_name}, Type: {ds.source_type}, Host: {ds.host}, User: {ds.username}")
    finally:
        await close_db()

if __name__ == "__main__":
    asyncio.run(check())
