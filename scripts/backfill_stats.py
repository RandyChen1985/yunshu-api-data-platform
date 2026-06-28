import asyncio
import os
import sys

# Ensure app path is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.jobs.aggregator import run_history_aggregation
from app.core import database

async def main():
    try:
        await database.init_db()
        # 回填过去 7 天的数据
        await run_history_aggregation(days=7)
    finally:
        await database.close_db()

if __name__ == "__main__":
    print("Starting backfill process...")
    asyncio.run(main())
    print("Done.")
